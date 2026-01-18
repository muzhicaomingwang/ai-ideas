import com.teamventure.app.service.XiaohongshuImportService;

public class PrintXhsParseShare2 {
  public static void main(String[] args) {
    XiaohongshuImportService service = new XiaohongshuImportService();
    String shareText = """
上海可以分为4个板块游玩不绕路✔️
#上海citywalk
精心划分四大板块，串联热门景点，不走回头路、不绕路
📝三日游精华路线
🏷️day1:南京路步行街-上海邮政博物馆-外白渡桥-乍浦路桥-和平饭店-外滩-陆家嘴-东方明珠
🏷️day2：愚园路-安福路-乌鲁木齐路-五原路-武康路-武康大楼
🏷️day3：静安寺-马勒别墅-淮海中路-思南公馆-上海新天地-上海博物馆
🚇 上海交通指南
1️⃣飞机：上海浦东国际机场/上海虹桥国际机场
2️⃣高铁：上海虹桥站
""";
    var resp = service.parse(shareText);
    System.out.println(resp.generatedMarkdown);
  }
}
