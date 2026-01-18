import com.teamventure.app.service.XiaohongshuImportService;
import com.teamventure.app.support.BizException;

public class PrintXhsParseShare {
  public static void main(String[] args) {
    XiaohongshuImportService service = new XiaohongshuImportService();
    String input = """
78 【上海可以分为4个板块游玩不绕路✔️ - 李小小爱旅行（攻略版） | 小红书 - 你的生活兴趣社区】 😆 HAGCtqi5iliiuu3 😆 https://www.xiaohongshu.com/discovery/item/695bbac4000000001a037a46?source=webshare&xhsshare=pc_web&xsec_token=AB5taFdJiFo4QiSl3j3-TiRMphDxMUG7hy9d6eY4HncwE=&xsec_source=pc_share
""";
    try {
      var resp = service.parse(input);
      System.out.println("OK\n" + resp.generatedMarkdown);
    } catch (BizException e) {
      System.out.println("BizException: code=" + e.getCode() + " message=" + e.getMessage());
    } catch (Exception e) {
      e.printStackTrace();
    }
  }
}
