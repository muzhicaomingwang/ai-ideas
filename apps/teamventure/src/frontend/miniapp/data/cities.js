/**
 * Static city data for TeamVenture miniapp
 * Provides provinces, cities, destinations, and countries for trip planning
 *
 * Data structure:
 * - CHINA_PROVINCES: All 34 provinces/municipalities/autonomous regions
 * - CHINA_CITIES: Cities organized by province
 * - POPULAR_DESTINATIONS: Tourist destinations organized by city
 * - COUNTRIES: International destinations
 */

// 34 Chinese provinces, municipalities, and autonomous regions
const CHINA_PROVINCES = [
  { id: 'beijing', name: '北京市', pinyin: 'beijing', type: 'municipality' },
  { id: 'shanghai', name: '上海市', pinyin: 'shanghai', type: 'municipality' },
  { id: 'tianjin', name: '天津市', pinyin: 'tianjin', type: 'municipality' },
  { id: 'chongqing', name: '重庆市', pinyin: 'chongqing', type: 'municipality' },
  { id: 'guangdong', name: '广东省', pinyin: 'guangdong', type: 'province' },
  { id: 'zhejiang', name: '浙江省', pinyin: 'zhejiang', type: 'province' },
  { id: 'jiangsu', name: '江苏省', pinyin: 'jiangsu', type: 'province' },
  { id: 'shandong', name: '山东省', pinyin: 'shandong', type: 'province' },
  { id: 'sichuan', name: '四川省', pinyin: 'sichuan', type: 'province' },
  { id: 'henan', name: '河南省', pinyin: 'henan', type: 'province' },
  { id: 'hebei', name: '河北省', pinyin: 'hebei', type: 'province' },
  { id: 'hubei', name: '湖北省', pinyin: 'hubei', type: 'province' },
  { id: 'hunan', name: '湖南省', pinyin: 'hunan', type: 'province' },
  { id: 'fujian', name: '福建省', pinyin: 'fujian', type: 'province' },
  { id: 'anhui', name: '安徽省', pinyin: 'anhui', type: 'province' },
  { id: 'liaoning', name: '辽宁省', pinyin: 'liaoning', type: 'province' },
  { id: 'shaanxi', name: '陕西省', pinyin: 'shaanxi', type: 'province' },
  { id: 'jiangxi', name: '江西省', pinyin: 'jiangxi', type: 'province' },
  { id: 'yunnan', name: '云南省', pinyin: 'yunnan', type: 'province' },
  { id: 'shanxi', name: '山西省', pinyin: 'shanxi', type: 'province' },
  { id: 'guangxi', name: '广西壮族自治区', pinyin: 'guangxi', type: 'autonomous-region' },
  { id: 'jilin', name: '吉林省', pinyin: 'jilin', type: 'province' },
  { id: 'heilongjiang', name: '黑龙江省', pinyin: 'heilongjiang', type: 'province' },
  { id: 'guizhou', name: '贵州省', pinyin: 'guizhou', type: 'province' },
  { id: 'gansu', name: '甘肃省', pinyin: 'gansu', type: 'province' },
  { id: 'inner-mongolia', name: '内蒙古自治区', pinyin: 'neimenggu', type: 'autonomous-region' },
  { id: 'xinjiang', name: '新疆维吾尔自治区', pinyin: 'xinjiang', type: 'autonomous-region' },
  { id: 'ningxia', name: '宁夏回族自治区', pinyin: 'ningxia', type: 'autonomous-region' },
  { id: 'hainan', name: '海南省', pinyin: 'hainan', type: 'province' },
  { id: 'tibet', name: '西藏自治区', pinyin: 'xizang', type: 'autonomous-region' },
  { id: 'qinghai', name: '青海省', pinyin: 'qinghai', type: 'province' },
  { id: 'hongkong', name: '香港特别行政区', pinyin: 'xianggang', type: 'special-region' },
  { id: 'macau', name: '澳门特别行政区', pinyin: 'aomen', type: 'special-region' },
  { id: 'taiwan', name: '台湾省', pinyin: 'taiwan', type: 'province' }
]

// Cities organized by province
const CHINA_CITIES = {
  'beijing': [
    { id: 'beijing-city', name: '北京市区', pinyin: 'beijingshiqu' }
  ],
  'shanghai': [
    { id: 'shanghai-city', name: '上海市区', pinyin: 'shanghshiqu' }
  ],
  'tianjin': [
    { id: 'tianjin-city', name: '天津市区', pinyin: 'tianjinshiqu' }
  ],
  'chongqing': [
    { id: 'chongqing-city', name: '重庆市区', pinyin: 'chongqingshiqu' }
  ],
  'guangdong': [
    { id: 'guangzhou', name: '广州市', pinyin: 'guangzhou' },
    { id: 'shenzhen', name: '深圳市', pinyin: 'shenzhen' },
    { id: 'zhuhai', name: '珠海市', pinyin: 'zhuhai' },
    { id: 'foshan', name: '佛山市', pinyin: 'foshan' },
    { id: 'dongguan', name: '东莞市', pinyin: 'dongguan' },
    { id: 'zhongshan', name: '中山市', pinyin: 'zhongshan' },
    { id: 'huizhou', name: '惠州市', pinyin: 'huizhou' },
    { id: 'jiangmen', name: '江门市', pinyin: 'jiangmen' },
    { id: 'zhanjiang', name: '湛江市', pinyin: 'zhanjiang' },
    { id: 'shantou', name: '汕头市', pinyin: 'shantou' },
    { id: 'shaoguan', name: '韶关市', pinyin: 'shaoguan' },
    { id: 'qingyuan', name: '清远市', pinyin: 'qingyuan' }
  ],
  'zhejiang': [
    { id: 'hangzhou', name: '杭州市', pinyin: 'hangzhou' },
    { id: 'ningbo', name: '宁波市', pinyin: 'ningbo' },
    { id: 'wenzhou', name: '温州市', pinyin: 'wenzhou' },
    { id: 'jiaxing', name: '嘉兴市', pinyin: 'jiaxing' },
    { id: 'huzhou', name: '湖州市', pinyin: 'huzhou' },
    { id: 'shaoxing', name: '绍兴市', pinyin: 'shaoxing' },
    { id: 'jinhua', name: '金华市', pinyin: 'jinhua' },
    { id: 'quzhou', name: '衢州市', pinyin: 'quzhou' },
    { id: 'taizhou-zj', name: '台州市', pinyin: 'taizhou' },
    { id: 'lishui', name: '丽水市', pinyin: 'lishui' },
    { id: 'zhoushan', name: '舟山市', pinyin: 'zhoushan' }
  ],
  'jiangsu': [
    { id: 'nanjing', name: '南京市', pinyin: 'nanjing' },
    { id: 'suzhou', name: '苏州市', pinyin: 'suzhou' },
    { id: 'wuxi', name: '无锡市', pinyin: 'wuxi' },
    { id: 'changzhou', name: '常州市', pinyin: 'changzhou' },
    { id: 'nantong', name: '南通市', pinyin: 'nantong' },
    { id: 'yangzhou', name: '扬州市', pinyin: 'yangzhou' },
    { id: 'xuzhou', name: '徐州市', pinyin: 'xuzhou' },
    { id: 'zhenjiang', name: '镇江市', pinyin: 'zhenjiang' },
    { id: 'taizhou-js', name: '泰州市', pinyin: 'taizhou' }
  ],
  'shandong': [
    { id: 'jinan', name: '济南市', pinyin: 'jinan' },
    { id: 'qingdao', name: '青岛市', pinyin: 'qingdao' },
    { id: 'yantai', name: '烟台市', pinyin: 'yantai' },
    { id: 'weifang', name: '潍坊市', pinyin: 'weifang' },
    { id: 'zibo', name: '淄博市', pinyin: 'zibo' },
    { id: 'weihai', name: '威海市', pinyin: 'weihai' },
    { id: 'taian', name: '泰安市', pinyin: 'taian' }
  ],
  'sichuan': [
    { id: 'chengdu', name: '成都市', pinyin: 'chengdu' },
    { id: 'mianyang', name: '绵阳市', pinyin: 'mianyang' },
    { id: 'deyang', name: '德阳市', pinyin: 'deyang' },
    { id: 'leshan', name: '乐山市', pinyin: 'leshan' },
    { id: 'yibin', name: '宜宾市', pinyin: 'yibin' }
  ],
  'henan': [
    { id: 'zhengzhou', name: '郑州市', pinyin: 'zhengzhou' },
    { id: 'luoyang', name: '洛阳市', pinyin: 'luoyang' },
    { id: 'kaifeng', name: '开封市', pinyin: 'kaifeng' },
    { id: 'anyang', name: '安阳市', pinyin: 'anyang' }
  ],
  'hebei': [
    { id: 'shijiazhuang', name: '石家庄市', pinyin: 'shijiazhuang' },
    { id: 'tangshan', name: '唐山市', pinyin: 'tangshan' },
    { id: 'qinhuangdao', name: '秦皇岛市', pinyin: 'qinhuangdao' },
    { id: 'baoding', name: '保定市', pinyin: 'baoding' },
    { id: 'zhangjiakou', name: '张家口市', pinyin: 'zhangjiakou' }
  ],
  'hubei': [
    { id: 'wuhan', name: '武汉市', pinyin: 'wuhan' },
    { id: 'yichang', name: '宜昌市', pinyin: 'yichang' },
    { id: 'xiangyang', name: '襄阳市', pinyin: 'xiangyang' }
  ],
  'hunan': [
    { id: 'changsha', name: '长沙市', pinyin: 'changsha' },
    { id: 'zhangjiajie', name: '张家界市', pinyin: 'zhangjiajie' },
    { id: 'hengyang', name: '衡阳市', pinyin: 'hengyang' },
    { id: 'xiangtan', name: '湘潭市', pinyin: 'xiangtan' }
  ],
  'fujian': [
    { id: 'fuzhou', name: '福州市', pinyin: 'fuzhou' },
    { id: 'xiamen', name: '厦门市', pinyin: 'xiamen' },
    { id: 'quanzhou', name: '泉州市', pinyin: 'quanzhou' },
    { id: 'zhangzhou', name: '漳州市', pinyin: 'zhangzhou' }
  ],
  'anhui': [
    { id: 'hefei', name: '合肥市', pinyin: 'hefei' },
    { id: 'wuhu', name: '芜湖市', pinyin: 'wuhu' },
    { id: 'huangshan', name: '黄山市', pinyin: 'huangshan' }
  ],
  'liaoning': [
    { id: 'shenyang', name: '沈阳市', pinyin: 'shenyang' },
    { id: 'dalian', name: '大连市', pinyin: 'dalian' },
    { id: 'anshan', name: '鞍山市', pinyin: 'anshan' }
  ],
  'shaanxi': [
    { id: 'xian', name: '西安市', pinyin: 'xian' },
    { id: 'baoji', name: '宝鸡市', pinyin: 'baoji' },
    { id: 'xianyang', name: '咸阳市', pinyin: 'xianyang' }
  ],
  'jiangxi': [
    { id: 'nanchang', name: '南昌市', pinyin: 'nanchang' },
    { id: 'jiujiang', name: '九江市', pinyin: 'jiujiang' },
    { id: 'ganzhou', name: '赣州市', pinyin: 'ganzhou' }
  ],
  'yunnan': [
    { id: 'kunming', name: '昆明市', pinyin: 'kunming' },
    { id: 'dali', name: '大理白族自治州', pinyin: 'dali' },
    { id: 'lijiang', name: '丽江市', pinyin: 'lijiang' },
    { id: 'xishuangbanna', name: '西双版纳傣族自治州', pinyin: 'xishuangbanna' }
  ],
  'shanxi': [
    { id: 'taiyuan', name: '太原市', pinyin: 'taiyuan' },
    { id: 'datong', name: '大同市', pinyin: 'datong' }
  ],
  'guangxi': [
    { id: 'nanning', name: '南宁市', pinyin: 'nanning' },
    { id: 'guilin', name: '桂林市', pinyin: 'guilin' },
    { id: 'beihai', name: '北海市', pinyin: 'beihai' }
  ],
  'jilin': [
    { id: 'changchun', name: '长春市', pinyin: 'changchun' },
    { id: 'jilinshi', name: '吉林市', pinyin: 'jilinshi' }
  ],
  'heilongjiang': [
    { id: 'haerbin', name: '哈尔滨市', pinyin: 'haerbin' },
    { id: 'qiqihaer', name: '齐齐哈尔市', pinyin: 'qiqihaer' }
  ],
  'guizhou': [
    { id: 'guiyang', name: '贵阳市', pinyin: 'guiyang' },
    { id: 'zunyi', name: '遵义市', pinyin: 'zunyi' }
  ],
  'gansu': [
    { id: 'lanzhou', name: '兰州市', pinyin: 'lanzhou' },
    { id: 'tianshui', name: '天水市', pinyin: 'tianshui' }
  ],
  'inner-mongolia': [
    { id: 'hohhot', name: '呼和浩特市', pinyin: 'huhehaote' },
    { id: 'baotou', name: '包头市', pinyin: 'baotou' }
  ],
  'xinjiang': [
    { id: 'urumqi', name: '乌鲁木齐市', pinyin: 'wulumuqi' }
  ],
  'ningxia': [
    { id: 'yinchuan', name: '银川市', pinyin: 'yinchuan' }
  ],
  'hainan': [
    { id: 'haikou', name: '海口市', pinyin: 'haikou' },
    { id: 'sanya', name: '三亚市', pinyin: 'sanya' }
  ],
  'tibet': [
    { id: 'lhasa', name: '拉萨市', pinyin: 'lasa' }
  ],
  'qinghai': [
    { id: 'xining', name: '西宁市', pinyin: 'xining' }
  ],
  'hongkong': [
    { id: 'hongkong-island', name: '香港岛', pinyin: 'xianggangdao' },
    { id: 'kowloon', name: '九龙', pinyin: 'jiulong' }
  ],
  'macau': [
    { id: 'macau-peninsula', name: '澳门半岛', pinyin: 'aomenbandao' }
  ],
  'taiwan': [
    { id: 'taipei', name: '台北市', pinyin: 'taibei' },
    { id: 'kaohsiung', name: '高雄市', pinyin: 'gaoxiong' }
  ]
}

// Popular destinations organized by city (for regional trips)
const POPULAR_DESTINATIONS = {
  'guangzhou': [
    { id: 'gz-conghua', name: '从化温泉', pinyin: 'conghua', type: 'resort' },
    { id: 'gz-changlong', name: '长隆度假区', pinyin: 'changlong', type: 'theme-park' },
    { id: 'gz-baiyun', name: '白云山', pinyin: 'baiyunshan', type: 'nature' },
    { id: 'gz-yuexiu', name: '越秀公园', pinyin: 'yuexiugongyuan', type: 'park' }
  ],
  'shenzhen': [
    { id: 'sz-dameisha', name: '大梅沙海滨公园', pinyin: 'dameisha', type: 'beach' },
    { id: 'sz-window', name: '世界之窗', pinyin: 'shijiezhichuang', type: 'theme-park' },
    { id: 'sz-splendid', name: '锦绣中华', pinyin: 'jinxiuzhonghua', type: 'culture' },
    { id: 'sz-dapeng', name: '大鹏半岛', pinyin: 'dapengbandao', type: 'nature' }
  ],
  'zhuhai': [
    { id: 'zh-chimelong', name: '长隆海洋王国', pinyin: 'changlonghaiyang', type: 'theme-park' },
    { id: 'zh-yuanming', name: '圆明新园', pinyin: 'yuanmingxinyuan', type: 'culture' },
    { id: 'zh-lover', name: '情侣路', pinyin: 'qinglvlu', type: 'scenic' }
  ],
  'hangzhou': [
    { id: 'hz-westlake', name: '西湖', pinyin: 'xihu', type: 'nature' },
    { id: 'hz-lingyin', name: '灵隐寺', pinyin: 'lingyinsi', type: 'temple' },
    { id: 'hz-qiandao', name: '千岛湖', pinyin: 'qiandaohu', type: 'lake' },
    { id: 'hz-xixi', name: '西溪湿地', pinyin: 'xixishidi', type: 'wetland' }
  ],
  'suzhou': [
    { id: 'sz-zhuozheng', name: '拙政园', pinyin: 'zhuozhengyuan', type: 'garden' },
    { id: 'sz-tongli', name: '同里古镇', pinyin: 'tongli', type: 'ancient-town' },
    { id: 'sz-taihu', name: '太湖', pinyin: 'taihu', type: 'lake' }
  ],
  'beijing-city': [
    { id: 'bj-badaling', name: '八达岭长城', pinyin: 'badaling', type: 'historic' },
    { id: 'bj-huairou', name: '怀柔雁栖湖', pinyin: 'huairou', type: 'lake' },
    { id: 'bj-miyun', name: '密云水库', pinyin: 'miyun', type: 'reservoir' }
  ],
  'shanghai-city': [
    { id: 'sh-zhujiajiao', name: '朱家角古镇', pinyin: 'zhujiajiao', type: 'ancient-town' },
    { id: 'sh-chongming', name: '崇明岛', pinyin: 'chongmingdao', type: 'island' },
    { id: 'sh-disneyland', name: '迪士尼乐园', pinyin: 'dishini', type: 'theme-park' }
  ],
  'chengdu': [
    { id: 'cd-qingcheng', name: '青城山', pinyin: 'qingchengshan', type: 'mountain' },
    { id: 'cd-dujiangyan', name: '都江堰', pinyin: 'dujiangyan', type: 'historic' },
    { id: 'cd-emei', name: '峨眉山', pinyin: 'emeishan', type: 'mountain' }
  ],
  'xian': [
    { id: 'xa-terracotta', name: '兵马俑', pinyin: 'bingmayong', type: 'historic' },
    { id: 'xa-huaqing', name: '华清池', pinyin: 'huaqingchi', type: 'historic' },
    { id: 'xa-huashan', name: '华山', pinyin: 'huashan', type: 'mountain' }
  ],
  'kunming': [
    { id: 'km-shilin', name: '石林', pinyin: 'shilin', type: 'nature' },
    { id: 'km-dianchi', name: '滇池', pinyin: 'dianchi', type: 'lake' }
  ],
  'lijiang': [
    { id: 'lj-oldtown', name: '丽江古城', pinyin: 'lijiangucheng', type: 'ancient-town' },
    { id: 'lj-yulong', name: '玉龙雪山', pinyin: 'yulongxueshan', type: 'mountain' }
  ],
  'guilin': [
    { id: 'gl-liriver', name: '漓江', pinyin: 'lijiang', type: 'river' },
    { id: 'gl-yangshuo', name: '阳朔', pinyin: 'yangshuo', type: 'town' }
  ],
  'sanya': [
    { id: 'sy-yalong', name: '亚龙湾', pinyin: 'yalongwan', type: 'beach' },
    { id: 'sy-tianya', name: '天涯海角', pinyin: 'tianyahaijiao', type: 'scenic' },
    { id: 'sy-wuzhizhou', name: '蜈支洲岛', pinyin: 'wuzhizhoudao', type: 'island' }
  ],
  'zhangjiajie': [
    { id: 'zjj-avatar', name: '张家界国家森林公园', pinyin: 'zhangjiajieguojiasenlinyuan', type: 'nature' },
    { id: 'zjj-tianmen', name: '天门山', pinyin: 'tianmenshan', type: 'mountain' }
  ],
  'huangshan': [
    { id: 'hs-mountain', name: '黄山风景区', pinyin: 'huangshan', type: 'mountain' },
    { id: 'hs-hongcun', name: '宏村', pinyin: 'hongcun', type: 'ancient-village' }
  ]
}

// International destinations (50+ popular countries)
const COUNTRIES = [
  // East Asia
  { id: 'japan', name: '日本', pinyin: 'riben', region: 'east-asia', popular: true },
  { id: 'south-korea', name: '韩国', pinyin: 'hanguo', region: 'east-asia', popular: true },

  // Southeast Asia
  { id: 'thailand', name: '泰国', pinyin: 'taiguo', region: 'southeast-asia', popular: true },
  { id: 'singapore', name: '新加坡', pinyin: 'xinjiapo', region: 'southeast-asia', popular: true },
  { id: 'malaysia', name: '马来西亚', pinyin: 'malaixiya', region: 'southeast-asia', popular: true },
  { id: 'vietnam', name: '越南', pinyin: 'yuenan', region: 'southeast-asia', popular: true },
  { id: 'philippines', name: '菲律宾', pinyin: 'feilvbin', region: 'southeast-asia', popular: false },
  { id: 'indonesia', name: '印度尼西亚', pinyin: 'yindunixiya', region: 'southeast-asia', popular: true },
  { id: 'cambodia', name: '柬埔寨', pinyin: 'jianpuzhai', region: 'southeast-asia', popular: false },
  { id: 'myanmar', name: '缅甸', pinyin: 'miandian', region: 'southeast-asia', popular: false },

  // South Asia
  { id: 'india', name: '印度', pinyin: 'yindu', region: 'south-asia', popular: false },
  { id: 'sri-lanka', name: '斯里兰卡', pinyin: 'sililanka', region: 'south-asia', popular: false },
  { id: 'maldives', name: '马尔代夫', pinyin: 'maerdaifu', region: 'south-asia', popular: true },

  // Oceania
  { id: 'australia', name: '澳大利亚', pinyin: 'aodaliya', region: 'oceania', popular: true },
  { id: 'new-zealand', name: '新西兰', pinyin: 'xinxilan', region: 'oceania', popular: true },
  { id: 'fiji', name: '斐济', pinyin: 'feiji', region: 'oceania', popular: false },

  // Europe
  { id: 'france', name: '法国', pinyin: 'faguo', region: 'europe', popular: true },
  { id: 'uk', name: '英国', pinyin: 'yingguo', region: 'europe', popular: true },
  { id: 'germany', name: '德国', pinyin: 'deguo', region: 'europe', popular: true },
  { id: 'italy', name: '意大利', pinyin: 'yidali', region: 'europe', popular: true },
  { id: 'spain', name: '西班牙', pinyin: 'xibanya', region: 'europe', popular: true },
  { id: 'switzerland', name: '瑞士', pinyin: 'ruishi', region: 'europe', popular: true },
  { id: 'netherlands', name: '荷兰', pinyin: 'helan', region: 'europe', popular: true },
  { id: 'belgium', name: '比利时', pinyin: 'bilishi', region: 'europe', popular: false },
  { id: 'austria', name: '奥地利', pinyin: 'aodili', region: 'europe', popular: false },
  { id: 'greece', name: '希腊', pinyin: 'xila', region: 'europe', popular: true },
  { id: 'portugal', name: '葡萄牙', pinyin: 'putaoya', region: 'europe', popular: false },
  { id: 'czech', name: '捷克', pinyin: 'jieke', region: 'europe', popular: false },
  { id: 'russia', name: '俄罗斯', pinyin: 'eluosi', region: 'europe', popular: true },
  { id: 'turkey', name: '土耳其', pinyin: 'tuerqi', region: 'europe', popular: true },

  // North America
  { id: 'usa', name: '美国', pinyin: 'meiguo', region: 'north-america', popular: true },
  { id: 'canada', name: '加拿大', pinyin: 'jianada', region: 'north-america', popular: true },
  { id: 'mexico', name: '墨西哥', pinyin: 'moxige', region: 'north-america', popular: false },

  // Central & South America
  { id: 'brazil', name: '巴西', pinyin: 'baxi', region: 'south-america', popular: false },
  { id: 'argentina', name: '阿根廷', pinyin: 'agenting', region: 'south-america', popular: false },
  { id: 'peru', name: '秘鲁', pinyin: 'milu', region: 'south-america', popular: false },
  { id: 'chile', name: '智利', pinyin: 'zhili', region: 'south-america', popular: false },

  // Middle East
  { id: 'uae', name: '阿联酋', pinyin: 'alianqiu', region: 'middle-east', popular: true },
  { id: 'israel', name: '以色列', pinyin: 'yiselie', region: 'middle-east', popular: false },
  { id: 'egypt', name: '埃及', pinyin: 'aiji', region: 'middle-east', popular: false },
  { id: 'morocco', name: '摩洛哥', pinyin: 'moluoge', region: 'middle-east', popular: false },

  // Africa
  { id: 'south-africa', name: '南非', pinyin: 'nanfei', region: 'africa', popular: false },
  { id: 'kenya', name: '肯尼亚', pinyin: 'kenniya', region: 'africa', popular: false },
  { id: 'tanzania', name: '坦桑尼亚', pinyin: 'tansangniya', region: 'africa', popular: false },
  { id: 'mauritius', name: '毛里求斯', pinyin: 'maoliqiusi', region: 'africa', popular: true }
]

/**
 * Helper functions
 */

/**
 * Get all provinces/municipalities
 * @returns {Array} Array of province objects
 */
function getProvinces() {
  return CHINA_PROVINCES
}

/**
 * Get cities for a specific province
 * @param {string} provinceId - Province ID
 * @returns {Array} Array of city objects
 */
function getCities(provinceId) {
  return CHINA_CITIES[provinceId] || []
}

/**
 * Get destinations for a specific city
 * @param {string} cityId - City ID
 * @returns {Array} Array of destination objects
 */
function getDestinations(cityId) {
  return POPULAR_DESTINATIONS[cityId] || []
}

/**
 * Get all countries
 * @param {boolean} popularOnly - Filter for popular countries only
 * @returns {Array} Array of country objects
 */
function getCountries(popularOnly = false) {
  if (popularOnly) {
    return COUNTRIES.filter(c => c.popular)
  }
  return COUNTRIES
}

/**
 * Search provinces by name or pinyin
 * @param {string} keyword - Search keyword
 * @returns {Array} Matching provinces
 */
function searchProvinces(keyword) {
  const lowerKeyword = keyword.toLowerCase()
  return CHINA_PROVINCES.filter(p =>
    p.name.includes(keyword) ||
    p.pinyin.includes(lowerKeyword)
  )
}

/**
 * Search cities by name or pinyin (across all provinces)
 * @param {string} keyword - Search keyword
 * @returns {Array} Matching cities with province info
 */
function searchCities(keyword) {
  const lowerKeyword = keyword.toLowerCase()
  const results = []

  Object.keys(CHINA_CITIES).forEach(provinceId => {
    const cities = CHINA_CITIES[provinceId]
    const matching = cities.filter(c =>
      c.name.includes(keyword) ||
      c.pinyin.includes(lowerKeyword)
    )

    matching.forEach(city => {
      const province = CHINA_PROVINCES.find(p => p.id === provinceId)
      results.push({
        ...city,
        provinceName: province ? province.name : ''
      })
    })
  })

  return results
}

/**
 * Search countries by name or pinyin
 * @param {string} keyword - Search keyword
 * @returns {Array} Matching countries
 */
function searchCountries(keyword) {
  const lowerKeyword = keyword.toLowerCase()
  return COUNTRIES.filter(c =>
    c.name.includes(keyword) ||
    c.pinyin.includes(lowerKeyword)
  )
}

module.exports = {
  getProvinces,
  getCities,
  getDestinations,
  getCountries,
  searchProvinces,
  searchCities,
  searchCountries,
  // Export raw data for advanced use cases
  CHINA_PROVINCES,
  CHINA_CITIES,
  POPULAR_DESTINATIONS,
  COUNTRIES
}
