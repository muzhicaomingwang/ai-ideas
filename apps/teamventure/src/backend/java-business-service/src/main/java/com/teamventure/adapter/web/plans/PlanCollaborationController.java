package com.teamventure.adapter.web.plans;

import com.teamventure.adapter.web.common.ApiResponse;
import com.teamventure.app.service.AuthService;
import com.teamventure.app.service.PlanCollaborationCommandService;
import com.teamventure.app.service.PlanCollaborationQueryService;
import com.teamventure.infrastructure.persistence.po.PlanItineraryRevisionPO;
import com.teamventure.infrastructure.persistence.po.PlanItinerarySuggestionPO;
import com.teamventure.infrastructure.persistence.po.PlanMembershipPO;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import java.util.List;
import java.util.Map;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1")
public class PlanCollaborationController {
    private final AuthService authService;
    private final PlanCollaborationCommandService collaborationCommandService;
    private final PlanCollaborationQueryService collaborationQueryService;

    public PlanCollaborationController(
            AuthService authService,
            PlanCollaborationCommandService collaborationCommandService,
            PlanCollaborationQueryService collaborationQueryService
    ) {
        this.authService = authService;
        this.collaborationCommandService = collaborationCommandService;
        this.collaborationQueryService = collaborationQueryService;
    }

    @PostMapping("/plans/{planId}/bookmark")
    public ApiResponse<Void> bookmark(
            @RequestHeader(value = "Authorization", required = false) String authorization,
            @PathVariable String planId
    ) {
        String userId = authService.getUserIdFromAuthorization(authorization);
        collaborationCommandService.bookmark(userId, planId);
        return ApiResponse.success();
    }

    @DeleteMapping("/plans/{planId}/bookmark")
    public ApiResponse<Void> unbookmark(
            @RequestHeader(value = "Authorization", required = false) String authorization,
            @PathVariable String planId
    ) {
        String userId = authService.getUserIdFromAuthorization(authorization);
        collaborationCommandService.unbookmark(userId, planId);
        return ApiResponse.success();
    }

    public static class ApplyRequest {
        public String apply_reason;
    }

    @PostMapping("/plans/{planId}/participation-applications")
    public ApiResponse<Void> apply(
            @RequestHeader(value = "Authorization", required = false) String authorization,
            @PathVariable String planId,
            @RequestBody(required = false) ApplyRequest req
    ) {
        String userId = authService.getUserIdFromAuthorization(authorization);
        collaborationCommandService.applyToParticipate(userId, planId, req == null ? null : req.apply_reason);
        return ApiResponse.success();
    }

    @PostMapping("/plans/{planId}/participation-applications/cancel")
    public ApiResponse<Void> cancel(
            @RequestHeader(value = "Authorization", required = false) String authorization,
            @PathVariable String planId
    ) {
        String userId = authService.getUserIdFromAuthorization(authorization);
        collaborationCommandService.cancelApplication(userId, planId);
        return ApiResponse.success();
    }

    @GetMapping("/plans/{planId}/participation-applications")
    public ApiResponse<List<PlanMembershipPO>> listApplications(
            @RequestHeader(value = "Authorization", required = false) String authorization,
            @PathVariable String planId
    ) {
        String userId = authService.getUserIdFromAuthorization(authorization);
        return ApiResponse.success(collaborationQueryService.listPendingApplications(userId, planId));
    }

    @PostMapping("/plans/{planId}/participation-applications/{userId}/approve")
    public ApiResponse<Void> approve(
            @RequestHeader(value = "Authorization", required = false) String authorization,
            @PathVariable String planId,
            @PathVariable String userId
    ) {
        String ownerId = authService.getUserIdFromAuthorization(authorization);
        collaborationCommandService.approveApplication(ownerId, planId, userId);
        return ApiResponse.success();
    }

    @PostMapping("/plans/{planId}/participation-applications/{userId}/reject")
    public ApiResponse<Void> reject(
            @RequestHeader(value = "Authorization", required = false) String authorization,
            @PathVariable String planId,
            @PathVariable String userId
    ) {
        String ownerId = authService.getUserIdFromAuthorization(authorization);
        collaborationCommandService.rejectApplication(ownerId, planId, userId);
        return ApiResponse.success();
    }

    @GetMapping("/plans/{planId}/members")
    public ApiResponse<List<PlanMembershipPO>> members(
            @RequestHeader(value = "Authorization", required = false) String authorization,
            @PathVariable String planId
    ) {
        String userId = authService.getUserIdFromAuthorization(authorization);
        return ApiResponse.success(collaborationQueryService.listMembers(userId, planId));
    }

    @PostMapping("/plans/{planId}/members/{userId}/remove")
    public ApiResponse<Void> remove(
            @RequestHeader(value = "Authorization", required = false) String authorization,
            @PathVariable String planId,
            @PathVariable String userId
    ) {
        String ownerId = authService.getUserIdFromAuthorization(authorization);
        collaborationCommandService.removeParticipant(ownerId, planId, userId);
        return ApiResponse.success();
    }

    @GetMapping("/plans/{planId}/itinerary/versions")
    public ApiResponse<List<PlanItineraryRevisionPO>> versions(
            @RequestHeader(value = "Authorization", required = false) String authorization,
            @PathVariable String planId
    ) {
        String userId = authService.getUserIdFromAuthorization(authorization);
        return ApiResponse.success(collaborationQueryService.listItineraryVersions(userId, planId));
    }

    @GetMapping("/plans/{planId}/itinerary/versions/{version}")
    public ApiResponse<Map<String, Object>> versionDetail(
            @RequestHeader(value = "Authorization", required = false) String authorization,
            @PathVariable String planId,
            @PathVariable int version
    ) {
        String userId = authService.getUserIdFromAuthorization(authorization);
        return ApiResponse.success(collaborationQueryService.getItineraryVersionDetail(userId, planId, version));
    }

    public static class CreateSuggestionRequest {
        @NotNull public Integer target_version;
        @NotBlank public String content;
    }

    @PostMapping("/plans/{planId}/itinerary-suggestions")
    public ApiResponse<Map<String, Object>> createSuggestion(
            @RequestHeader(value = "Authorization", required = false) String authorization,
            @PathVariable String planId,
            @Valid @RequestBody CreateSuggestionRequest req
    ) {
        String userId = authService.getUserIdFromAuthorization(authorization);
        return ApiResponse.success(collaborationCommandService.createSuggestion(userId, planId, req.target_version, req.content));
    }

    @GetMapping("/plans/{planId}/itinerary-suggestions")
    public ApiResponse<List<PlanItinerarySuggestionPO>> listSuggestions(
            @RequestHeader(value = "Authorization", required = false) String authorization,
            @PathVariable String planId,
            @RequestParam(required = false) Integer target_version
    ) {
        String userId = authService.getUserIdFromAuthorization(authorization);
        return ApiResponse.success(collaborationQueryService.listSuggestions(userId, planId, target_version));
    }

    public static class UpdateSuggestionRequest {
        @NotBlank public String content;
    }

    @PatchMapping("/itinerary-suggestions/{suggestionId}")
    public ApiResponse<Void> updateSuggestion(
            @RequestHeader(value = "Authorization", required = false) String authorization,
            @PathVariable String suggestionId,
            @Valid @RequestBody UpdateSuggestionRequest req
    ) {
        String userId = authService.getUserIdFromAuthorization(authorization);
        collaborationCommandService.updateOwnSuggestion(userId, suggestionId, req.content);
        return ApiResponse.success();
    }

    @DeleteMapping("/itinerary-suggestions/{suggestionId}")
    public ApiResponse<Void> deleteSuggestion(
            @RequestHeader(value = "Authorization", required = false) String authorization,
            @PathVariable String suggestionId
    ) {
        String userId = authService.getUserIdFromAuthorization(authorization);
        collaborationCommandService.deleteOwnSuggestion(userId, suggestionId);
        return ApiResponse.success();
    }
}
