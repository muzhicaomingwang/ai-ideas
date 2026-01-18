import com.teamventure.app.service.XiaohongshuImportService;
import com.teamventure.app.support.BizException;

public class PrintXhsParseUrl {
  public static void main(String[] args) {
    XiaohongshuImportService service = new XiaohongshuImportService();
    String url = "https://www.xiaohongshu.com/explore/695bbac4000000001a037a46?xsec_token=AB5taFdJiFo4QiSl3j3-TiRMphDxMUG7hy9d6eY4HncwE=&xsec_source=pc_search&source=unknown";
    try {
      var resp = service.parse(url);
      System.out.println("OK\n" + resp.generatedMarkdown);
    } catch (BizException e) {
      System.out.println("BizException: code=" + e.getCode() + " message=" + e.getMessage());
    } catch (Exception e) {
      e.printStackTrace();
    }
  }
}
