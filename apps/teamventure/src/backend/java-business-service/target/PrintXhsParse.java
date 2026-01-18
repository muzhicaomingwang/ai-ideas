import com.teamventure.app.service.XiaohongshuImportService;

public class PrintXhsParse {
  public static void main(String[] args) {
    XiaohongshuImportService service = new XiaohongshuImportService();
    String input = """
三亚5天4夜行程安排
D1 抵达三亚｜酒店办理入住｜椰梦长廊散步
D2 蜈支洲岛一日游｜浮潜｜海鲜大餐
D3 亚特兰蒂斯水世界｜免税店
Tips：防晒、提前预约
""";
    var resp = service.parse(input);
    System.out.println(resp.generatedMarkdown);
  }
}
