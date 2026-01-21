package com.teamventure.app.service;

import com.teamventure.app.support.BizException;
import com.teamventure.app.support.IdGenerator;
import io.minio.GetPresignedObjectUrlArgs;
import io.minio.MinioClient;
import io.minio.PutObjectArgs;
import io.minio.http.Method;
import java.io.ByteArrayInputStream;
import java.io.InputStream;
import java.util.Locale;
import java.util.Objects;
import java.util.concurrent.TimeUnit;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

@Service
public class OssService {
    private static final Logger log = LoggerFactory.getLogger(OssService.class);

    public enum Category {
        AVATAR,
        ITINERARY
    }

    public record UploadResult(
            Category category,
            String bucket,
            String objectKey,
            String url,
            boolean publicReadable
    ) {}

    private static final long MAX_IMAGE_BYTES = 10L * 1024 * 1024;

    private final MinioClient minio;
    private final MinioClient presignClient;
    private final String bucketAvatars;
    private final String bucketItinerary;
    private final String publicBaseUrl;
    private final int presignExpirySeconds;
    private final boolean avatarsPublic;

    public OssService(
            @Value("${TEAMVENTURE_OSS_ENDPOINT:http://minio:9000}") String endpoint,
            @Value("${TEAMVENTURE_OSS_PRESIGN_ENDPOINT:}") String presignEndpoint,
            @Value("${TEAMVENTURE_OSS_ACCESS_KEY:minioadmin}") String accessKey,
            @Value("${TEAMVENTURE_OSS_SECRET_KEY:minioadmin123456}") String secretKey,
            @Value("${MINIO_BUCKET_AVATARS:avatars}") String bucketAvatars,
            @Value("${MINIO_BUCKET_ITINERARY:itinerary}") String bucketItinerary,
            @Value("${MINIO_BUCKET_AVATARS_PUBLIC:0}") int avatarsPublic,
            @Value("${TEAMVENTURE_OSS_PUBLIC_BASE_URL:https://api.teamventure.com/oss}") String publicBaseUrl,
            @Value("${TEAMVENTURE_OSS_PRESIGN_EXPIRY_SECONDS:3600}") int presignExpirySeconds
    ) {
        this.minio = MinioClient.builder().endpoint(endpoint).credentials(accessKey, secretKey).build();
        String p = (presignEndpoint == null || presignEndpoint.isBlank()) ? endpoint : presignEndpoint;
        this.presignClient = MinioClient.builder().endpoint(p).credentials(accessKey, secretKey).build();
        this.bucketAvatars = bucketAvatars;
        this.bucketItinerary = bucketItinerary;
        this.publicBaseUrl = publicBaseUrl.endsWith("/") ? publicBaseUrl.substring(0, publicBaseUrl.length() - 1) : publicBaseUrl;
        this.presignExpirySeconds = presignExpirySeconds;
        this.avatarsPublic = avatarsPublic == 1;
    }

    public UploadResult uploadImage(String userId, Category category, MultipartFile file, String scope) {
        if (file == null || file.isEmpty()) {
            throw new BizException("BAD_REQUEST", "missing file");
        }
        if (file.getSize() > MAX_IMAGE_BYTES) {
            throw new BizException("BAD_REQUEST", "file too large");
        }
        String contentType = file.getContentType();
        if (contentType == null || !contentType.toLowerCase(Locale.ROOT).startsWith("image/")) {
            throw new BizException("BAD_REQUEST", "only image is allowed");
        }

        String ext = guessExt(file.getOriginalFilename(), contentType);
        String id = IdGenerator.newId("obj");
        String bucket = bucketFor(category);
        String objectKey = objectKeyFor(userId, category, scope, id, ext);

        try (InputStream in = file.getInputStream()) {
            minio.putObject(
                    PutObjectArgs.builder()
                            .bucket(bucket)
                            .object(objectKey)
                            .stream(in, file.getSize(), -1)
                            .contentType(contentType)
                            .build()
            );
        } catch (Exception e) {
            throw new BizException("OSS_UPLOAD_FAILED", "upload failed");
        }

        boolean isPublic = category == Category.ITINERARY || (category == Category.AVATAR && avatarsPublic);
        String url = isPublic ? publicUrl(bucket, objectKey) : presignGet(bucket, objectKey);
        return new UploadResult(category, bucket, objectKey, url, isPublic);
    }

    public UploadResult uploadImageBytes(Category category, byte[] bytes, String contentType, String scope, String filenameHint) {
        if (category != Category.ITINERARY) {
            throw new BizException("BAD_REQUEST", "only itinerary image bytes upload is supported");
        }
        if (bytes == null || bytes.length == 0) {
            throw new BizException("BAD_REQUEST", "missing bytes");
        }
        if (bytes.length > MAX_IMAGE_BYTES) {
            throw new BizException("BAD_REQUEST", "file too large");
        }
        String ct = (contentType == null ? "" : contentType).trim();
        int semicolon = ct.indexOf(';');
        if (semicolon >= 0) ct = ct.substring(0, semicolon).trim();
        ct = ct.toLowerCase(Locale.ROOT);
        if (!ct.startsWith("image/")) {
            throw new BizException("BAD_REQUEST", "only image is allowed");
        }

        String ext = guessExt(filenameHint, ct);
        String id = IdGenerator.newId("obj");
        String bucket = bucketFor(category);
        String objectKey = objectKeyFor("", category, scope, id, ext);

        try (InputStream in = new ByteArrayInputStream(bytes)) {
            minio.putObject(
                    PutObjectArgs.builder()
                            .bucket(bucket)
                            .object(objectKey)
                            .stream(in, bytes.length, -1)
                            .contentType(ct)
                            .build()
            );
        } catch (Exception e) {
            throw new BizException("OSS_UPLOAD_FAILED", "upload failed");
        }

        String url = publicUrl(bucket, objectKey);
        return new UploadResult(category, bucket, objectKey, url, true);
    }

    public String presignGet(String bucket, String objectKey) {
        try {
            return presignClient.getPresignedObjectUrl(
                    GetPresignedObjectUrlArgs.builder()
                            .method(Method.GET)
                            .bucket(bucket)
                            .object(objectKey)
                            .expiry(presignExpirySeconds, TimeUnit.SECONDS)
                            .build()
            );
        } catch (Exception e) {
            log.warn("oss presign failed: bucket={}, key={}", bucket, objectKey, e);
            throw new BizException("OSS_PRESIGN_FAILED", "presign failed");
        }
    }

    public String resolveAvatarUrl(String userId, String avatarUrl) {
        if (avatarUrl == null || avatarUrl.isBlank()) return "";
        String normalized = avatarUrl.trim();
        if (normalized.startsWith("http://") || normalized.startsWith("https://")) {
            return normalized;
        }
        String prefix = "minio://avatars/";
        if (!normalized.startsWith(prefix)) {
            return "";
        }
        String key = normalized.substring(prefix.length());
        String expectedPrefix = "users/" + userId + "/";
        if (!key.startsWith(expectedPrefix)) {
            return "";
        }
        return avatarsPublic ? publicUrl(bucketAvatars, key) : presignGet(bucketAvatars, key);
    }

    public String toAvatarStorageValue(String userId, String objectKey) {
        String expectedPrefix = "users/" + userId + "/";
        if (!Objects.requireNonNull(objectKey).startsWith(expectedPrefix)) {
            throw new BizException("BAD_REQUEST", "invalid avatar key");
        }
        return "minio://avatars/" + objectKey;
    }

    public String toItineraryStorageValue(String bucket, String objectKey) {
        String b = (bucket == null ? "" : bucket).trim();
        String k = (objectKey == null ? "" : objectKey).trim();
        if (b.isBlank() || k.isBlank()) {
            throw new BizException("BAD_REQUEST", "invalid itinerary key");
        }
        if (!b.equals(bucketItinerary)) {
            throw new BizException("BAD_REQUEST", "invalid itinerary bucket");
        }
        if (k.contains("..") || k.startsWith("/") || k.startsWith("\\")) {
            throw new BizException("BAD_REQUEST", "invalid itinerary key");
        }
        return "minio://" + b + "/" + k;
    }

    public String resolveItineraryUrl(String stored) {
        if (stored == null || stored.isBlank()) return "";
        String normalized = stored.trim();
        if (normalized.startsWith("http://") || normalized.startsWith("https://")) {
            return normalized;
        }
        String prefix = "minio://";
        if (!normalized.startsWith(prefix)) return "";
        String rest = normalized.substring(prefix.length());
        int slash = rest.indexOf('/');
        if (slash <= 0 || slash >= rest.length() - 1) return "";
        String bucket = rest.substring(0, slash);
        String key = rest.substring(slash + 1);
        if (!bucket.equals(bucketItinerary)) return "";
        if (key.contains("..") || key.startsWith("/") || key.startsWith("\\")) return "";
        return publicUrl(bucket, key);
    }

    private String bucketFor(Category category) {
        return switch (category) {
            case AVATAR -> bucketAvatars;
            case ITINERARY -> bucketItinerary;
        };
    }

    private String objectKeyFor(String userId, Category category, String scope, String id, String ext) {
        String safeExt = ext == null || ext.isBlank() ? "bin" : ext;
        return switch (category) {
            case AVATAR -> "users/" + userId + "/avatars/" + id + "." + safeExt;
            case ITINERARY -> {
                String safeScope = (scope == null || scope.isBlank()) ? "general" : sanitizePath(scope);
                yield "itinerary/" + safeScope + "/" + id + "." + safeExt;
            }
        };
    }

    private String sanitizePath(String v) {
        String s = v.trim().replace("\\", "/");
        while (s.startsWith("/")) s = s.substring(1);
        s = s.replace("..", "_");
        return s.replaceAll("[^a-zA-Z0-9/_-]", "_");
    }

    private String publicUrl(String bucket, String objectKey) {
        return publicBaseUrl + "/" + bucket + "/" + objectKey;
    }

    private String guessExt(String filename, String contentType) {
        String ext = null;
        if (filename != null) {
            int i = filename.lastIndexOf('.');
            if (i >= 0 && i < filename.length() - 1) {
                ext = filename.substring(i + 1).toLowerCase(Locale.ROOT);
            }
        }
        if (ext == null || ext.isBlank()) {
            ext = switch (contentType.toLowerCase(Locale.ROOT)) {
                case "image/jpeg" -> "jpg";
                case "image/png" -> "png";
                case "image/webp" -> "webp";
                case "image/gif" -> "gif";
                default -> "bin";
            };
        }
        return ext;
    }
}
