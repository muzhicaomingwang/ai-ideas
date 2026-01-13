// 省市区三级联动数据
// 注: 这是简化版本，包含常见的旅游目的地省份和城市
// 生产环境可以使用完整的行政区划数据或通过API动态加载

export const PROVINCES = [
  {
    name: '浙江省',
    code: '330000',
    cities: [
      {
        name: '杭州市',
        code: '330100',
        districts: [
          { name: '西湖区', code: '330106' },
          { name: '西溪湿地', code: '330106-1' },
          { name: '千岛湖', code: '330127-1' },
          { name: '桐庐县', code: '330122' }
        ]
      },
      {
        name: '宁波市',
        code: '330200',
        districts: [
          { name: '鄞州区', code: '330212' },
          { name: '象山县', code: '330225' },
          { name: '宁海县', code: '330226' }
        ]
      },
      {
        name: '湖州市',
        code: '330500',
        districts: [
          { name: '莫干山', code: '330521-1' },
          { name: '安吉县', code: '330523' },
          { name: '南浔古镇', code: '330503-1' }
        ]
      }
    ]
  },
  {
    name: '江苏省',
    code: '320000',
    cities: [
      {
        name: '苏州市',
        code: '320500',
        districts: [
          { name: '姑苏区', code: '320508' },
          { name: '周庄古镇', code: '320583-1' },
          { name: '同里古镇', code: '320509-1' },
          { name: '太湖景区', code: '320505-1' }
        ]
      },
      {
        name: '南京市',
        code: '320100',
        districts: [
          { name: '玄武区', code: '320102' },
          { name: '栖霞山', code: '320113-1' },
          { name: '中山陵', code: '320104-1' }
        ]
      },
      {
        name: '无锡市',
        code: '320200',
        districts: [
          { name: '滨湖区', code: '320211' },
          { name: '鼋头渚', code: '320211-1' },
          { name: '灵山大佛', code: '320213-1' }
        ]
      }
    ]
  },
  {
    name: '广东省',
    code: '440000',
    cities: [
      {
        name: '深圳市',
        code: '440300',
        districts: [
          { name: '南山区', code: '440305' },
          { name: '大鹏新区', code: '440307-1' },
          { name: '东部华侨城', code: '440308-1' }
        ]
      },
      {
        name: '广州市',
        code: '440100',
        districts: [
          { name: '天河区', code: '440106' },
          { name: '白云山', code: '440111-1' },
          { name: '长隆旅游度假区', code: '440113-1' }
        ]
      },
      {
        name: '珠海市',
        code: '440400',
        districts: [
          { name: '香洲区', code: '440402' },
          { name: '东澳岛', code: '440421-1' },
          { name: '外伶仃岛', code: '440421-2' }
        ]
      }
    ]
  },
  {
    name: '云南省',
    code: '530000',
    cities: [
      {
        name: '大理白族自治州',
        code: '532900',
        districts: [
          { name: '大理古城', code: '532901-1' },
          { name: '洱海', code: '532901-2' },
          { name: '双廊古镇', code: '532932-1' }
        ]
      },
      {
        name: '丽江市',
        code: '530700',
        districts: [
          { name: '古城区', code: '530702' },
          { name: '玉龙雪山', code: '530721-1' },
          { name: '束河古镇', code: '530702-1' }
        ]
      },
      {
        name: '西双版纳傣族自治州',
        code: '532800',
        districts: [
          { name: '景洪市', code: '532801' },
          { name: '中科院热带植物园', code: '532822-1' },
          { name: '野象谷', code: '532801-1' }
        ]
      }
    ]
  },
  {
    name: '四川省',
    code: '510000',
    cities: [
      {
        name: '成都市',
        code: '510100',
        districts: [
          { name: '武侯区', code: '510107' },
          { name: '青城山', code: '510181-1' },
          { name: '都江堰', code: '510181-2' }
        ]
      },
      {
        name: '阿坝藏族羌族自治州',
        code: '513200',
        districts: [
          { name: '九寨沟县', code: '513225' },
          { name: '黄龙景区', code: '513231-1' },
          { name: '四姑娘山', code: '513221-1' }
        ]
      }
    ]
  },
  {
    name: '海南省',
    code: '460000',
    cities: [
      {
        name: '三亚市',
        code: '460200',
        districts: [
          { name: '天涯区', code: '460204' },
          { name: '亚龙湾', code: '460203-1' },
          { name: '蜈支洲岛', code: '460202-1' },
          { name: '南山文化旅游区', code: '460204-1' }
        ]
      },
      {
        name: '海口市',
        code: '460100',
        districts: [
          { name: '龙华区', code: '460106' },
          { name: '假日海滩', code: '460105-1' },
          { name: '火山口地质公园', code: '460107-1' }
        ]
      }
    ]
  },
  {
    name: '安徽省',
    code: '340000',
    cities: [
      {
        name: '黄山市',
        code: '341000',
        districts: [
          { name: '黄山风景区', code: '341003-1' },
          { name: '宏村', code: '341023-1' },
          { name: '西递', code: '341023-2' }
        ]
      },
      {
        name: '合肥市',
        code: '340100',
        districts: [
          { name: '蜀山区', code: '340104' },
          { name: '三河古镇', code: '340122-1' }
        ]
      }
    ]
  },
  {
    name: '福建省',
    code: '350000',
    cities: [
      {
        name: '厦门市',
        code: '350200',
        districts: [
          { name: '思明区', code: '350203' },
          { name: '鼓浪屿', code: '350203-1' },
          { name: '曾厝垵', code: '350203-2' }
        ]
      },
      {
        name: '福州市',
        code: '350100',
        districts: [
          { name: '鼓楼区', code: '350102' },
          { name: '三坊七巷', code: '350102-1' }
        ]
      }
    ]
  }
]

// 根据省份名称获取城市列表
export function getCitiesByProvinceName(provinceName) {
  const province = PROVINCES.find(p => p.name === provinceName)
  return province ? province.cities : []
}

// 根据省份名称和城市名称获取区县列表
export function getDistrictsByCityName(provinceName, cityName) {
  const province = PROVINCES.find(p => p.name === provinceName)
  if (!province) return []

  const city = province.cities.find(c => c.name === cityName)
  return city ? city.districts : []
}
