// 模拟测试数据 - 用于本地测试

/**
 * 模拟方案数据
 */
export const mockPlans = [
  {
    plan_id: 'plan_mock_001',
    plan_name: '经济实惠·怀柔山野团建',
    plan_type: 'budget',
    status: 'draft',
    budget_total: 35000,
    people_count: 50,
    start_date: '2025-05-10',
    end_date: '2025-05-11',
    duration_days: 2,
    recommended: false,
    highlight: '适合预算有限的团队，在怀柔山区进行真人CS和徒步活动，体验农家菜和篝火晚会，性价比超高。',
    suitable_for: ['预算有限', '注重性价比', '喜欢户外'],
    preferences: {
      activity_types: ['team_building', 'outdoor'],
      accommodation_level: 'budget',
      dining_style: ['local']
    },
    itinerary: {
      days: [
        {
          day: 1,
          date: '2025-05-10（周六）',
          items: [
            {
              time_start: '08:30',
              time_end: '09:00',
              activity: '公司集合，统一大巴出发',
              location: '公司楼下',
              note: '请提前10分钟到达'
            },
            {
              time_start: '09:00',
              time_end: '11:00',
              activity: '前往目的地',
              location: '大巴车上'
            },
            {
              time_start: '11:00',
              time_end: '12:00',
              activity: '酒店check-in，行李寄存',
              location: '怀柔山庄'
            },
            {
              time_start: '12:00',
              time_end: '13:30',
              activity: '午餐：农家菜',
              location: '餐厅',
              note: '预算 ¥50/人'
            },
            {
              time_start: '13:30',
              time_end: '16:30',
              activity: '团队拓展活动：真人CS对抗赛',
              location: '拓展基地',
              note: '教练：2人'
            },
            {
              time_start: '16:30',
              time_end: '18:00',
              activity: '自由活动 / 湖边漫步',
              location: '度假村周边'
            },
            {
              time_start: '18:00',
              time_end: '20:00',
              activity: '晚餐 + 团队游戏',
              location: '餐厅'
            },
            {
              time_start: '20:00',
              time_end: '21:30',
              activity: '篝火晚会',
              location: '户外活动区'
            },
            {
              time_start: '21:30',
              time_end: '',
              activity: '回房间休息',
              location: '住宿区'
            }
          ]
        },
        {
          day: 2,
          date: '2025-05-11（周日）',
          items: [
            {
              time_start: '08:00',
              time_end: '09:00',
              activity: '早餐',
              location: '餐厅'
            },
            {
              time_start: '09:00',
              time_end: '11:30',
              activity: '户外徒步 / 团队协作游戏',
              location: '山间小道'
            },
            {
              time_start: '11:30',
              time_end: '13:00',
              activity: '午餐',
              location: '餐厅'
            },
            {
              time_start: '13:00',
              time_end: '15:00',
              activity: '返程',
              location: '大巴车上'
            },
            {
              time_start: '15:00',
              time_end: '',
              activity: '到达公司，活动结束',
              location: '公司'
            }
          ]
        }
      ]
    },
    budget_breakdown: {
      categories: [
        {
          category: '交通',
          items: [
            {
              item: '大巴往返',
              quantity: '1辆 x 2天',
              unit_price: 2000,
              total: 4000
            }
          ],
          subtotal: 4000
        },
        {
          category: '住宿',
          items: [
            {
              item: '农家乐（6人间）',
              quantity: '9间 x 1晚',
              unit_price: 150,
              total: 7500
            }
          ],
          subtotal: 7500
        },
        {
          category: '餐饮',
          items: [
            {
              item: '第一天午餐',
              quantity: '50人',
              unit_price: 50,
              total: 2500
            },
            {
              item: '第一天晚餐',
              quantity: '50人',
              unit_price: 80,
              total: 4000
            },
            {
              item: '第二天早餐',
              quantity: '50人',
              unit_price: 30,
              total: 1500
            },
            {
              item: '第二天午餐',
              quantity: '50人',
              unit_price: 50,
              total: 2500
            }
          ],
          subtotal: 10500
        },
        {
          category: '活动',
          items: [
            {
              item: '真人CS对抗赛',
              quantity: '50人',
              unit_price: 80,
              total: 4000
            },
            {
              item: '拓展教练费',
              quantity: '2人 x 3小时',
              unit_price: 200,
              total: 1200
            },
            {
              item: '篝火晚会',
              quantity: '1场',
              unit_price: 1500,
              total: 1500
            }
          ],
          subtotal: 6700
        },
        {
          category: '其他',
          items: [
            {
              item: '物料/应急费用',
              quantity: '1批',
              unit_price: 1300,
              total: 1300
            }
          ],
          subtotal: 1300
        }
      ],
      total: 30000,
      per_person: 600
    },
    suppliers: [
      {
        supplier_id: 'sup_001',
        name: '怀柔山庄',
        category: 'accommodation',
        rating: 4.5,
        price_range_min: 150,
        price_range_max: 300,
        contact_phone: '13800138001',
        contact_wechat: 'huairou_shanzhuan',
        tags: ['适合拓展', '环境优美', '性价比高']
      },
      {
        supplier_id: 'sup_002',
        name: '真人CS拓展基地',
        category: 'activity',
        rating: 4.8,
        price_range_min: 80,
        price_range_max: 150,
        contact_phone: '13800138002',
        contact_wechat: 'cs_base_hr',
        tags: ['专业教练', '场地大', '设备齐全']
      },
      {
        supplier_id: 'sup_003',
        name: '农家乐餐厅',
        category: 'dining',
        rating: 4.3,
        price_range_min: 30,
        price_range_max: 100,
        contact_phone: '13800138003',
        contact_wechat: 'farm_food_hr',
        tags: ['地道农家菜', '食材新鲜', '价格实惠']
      }
    ],
    created_at: '2025-01-02T10:30:00Z',
    generated_at: '2025-01-02T10:30:45Z'
  },
  {
    plan_id: 'plan_mock_002',
    plan_name: '平衡之选·密云水库度假',
    plan_type: 'standard',
    status: 'draft',
    budget_total: 45000,
    people_count: 50,
    start_date: '2025-05-10',
    end_date: '2025-05-11',
    duration_days: 2,
    recommended: true,
    highlight: '性价比高，民宿住宿舒适，活动丰富多样，适合大多数团队的需求。',
    suitable_for: ['性价比优先', '体验均衡', '注重舒适'],
    preferences: {
      activity_types: ['team_building', 'leisure'],
      accommodation_level: 'standard',
      dining_style: ['local', 'bbq']
    },
    itinerary: {
      days: [
        {
          day: 1,
          date: '2025-05-10（周六）',
          items: [
            {
              time_start: '08:30',
              time_end: '09:00',
              activity: '公司集合，统一大巴出发',
              location: '公司楼下'
            },
            {
              time_start: '09:00',
              time_end: '11:30',
              activity: '前往密云水库',
              location: '大巴车上'
            },
            {
              time_start: '11:30',
              time_end: '12:30',
              activity: '民宿check-in',
              location: '水库湖景民宿'
            },
            {
              time_start: '12:30',
              time_end: '14:00',
              activity: '午餐：特色鱼宴',
              location: '民宿餐厅'
            },
            {
              time_start: '14:00',
              time_end: '17:00',
              activity: '团队拓展：定向越野 + 团队协作',
              location: '水库周边'
            },
            {
              time_start: '17:00',
              time_end: '18:30',
              activity: '自由活动 / 湖边摄影',
              location: '水库边'
            },
            {
              time_start: '18:30',
              time_end: '20:30',
              activity: '晚餐BBQ + 团队聚餐',
              location: '户外烧烤区'
            },
            {
              time_start: '20:30',
              time_end: '',
              activity: '自由活动 / 休息',
              location: '民宿'
            }
          ]
        },
        {
          day: 2,
          date: '2025-05-11（周日）',
          items: [
            {
              time_start: '08:00',
              time_end: '09:00',
              activity: '早餐（民宿自助餐）',
              location: '民宿餐厅'
            },
            {
              time_start: '09:00',
              time_end: '11:30',
              activity: '皮划艇体验 / 团队游戏',
              location: '水库'
            },
            {
              time_start: '11:30',
              time_end: '13:00',
              activity: '午餐',
              location: '民宿餐厅'
            },
            {
              time_start: '13:00',
              time_end: '15:30',
              activity: '返程',
              location: '大巴车上'
            },
            {
              time_start: '15:30',
              time_end: '',
              activity: '到达公司，活动结束',
              location: '公司'
            }
          ]
        }
      ]
    },
    budget_breakdown: {
      categories: [
        {
          category: '交通',
          items: [
            { item: '大巴往返', quantity: '1辆 x 2天', unit_price: 2500, total: 5000 }
          ],
          subtotal: 5000
        },
        {
          category: '住宿',
          items: [
            { item: '民宿（2人间）', quantity: '25间 x 1晚', unit_price: 400, total: 10000 }
          ],
          subtotal: 10000
        },
        {
          category: '餐饮',
          items: [
            { item: '第一天午餐', quantity: '50人', unit_price: 80, total: 4000 },
            { item: '第一天晚餐BBQ', quantity: '50人', unit_price: 120, total: 6000 },
            { item: '第二天早餐', quantity: '50人', unit_price: 40, total: 2000 },
            { item: '第二天午餐', quantity: '50人', unit_price: 60, total: 3000 }
          ],
          subtotal: 15000
        },
        {
          category: '活动',
          items: [
            { item: '定向越野活动', quantity: '50人', unit_price: 100, total: 5000 },
            { item: '皮划艇体验', quantity: '50人', unit_price: 120, total: 6000 },
            { item: '教练及设备费', quantity: '1批', unit_price: 2000, total: 2000 }
          ],
          subtotal: 13000
        },
        {
          category: '其他',
          items: [
            { item: '物料/应急', quantity: '1批', unit_price: 2000, total: 2000 }
          ],
          subtotal: 2000
        }
      ],
      total: 45000,
      per_person: 900
    },
    suppliers: [
      {
        supplier_id: 'sup_004',
        name: '密云水库湖景民宿',
        category: 'accommodation',
        rating: 4.7,
        price_range_min: 300,
        price_range_max: 500,
        contact_phone: '13800138004',
        contact_wechat: 'miyun_lakehouse',
        tags: ['湖景房', '设施齐全', '环境优美']
      },
      {
        supplier_id: 'sup_005',
        name: '水库户外拓展中心',
        category: 'activity',
        rating: 4.6,
        price_range_min: 100,
        price_range_max: 200,
        contact_phone: '13800138005',
        contact_wechat: 'outdoor_miyun',
        tags: ['专业团队', '项目丰富', '安全保障']
      }
    ],
    created_at: '2025-01-02T10:30:00Z',
    generated_at: '2025-01-02T10:30:45Z'
  },
  {
    plan_id: 'plan_mock_003',
    plan_name: '品质体验·古北水镇团建',
    plan_type: 'premium',
    status: 'draft',
    budget_total: 60000,
    people_count: 50,
    start_date: '2025-05-10',
    end_date: '2025-05-11',
    duration_days: 2,
    recommended: false,
    highlight: '精品度假酒店，特色主题活动，精致餐饮体验，适合预算充足、注重品质的团队。',
    suitable_for: ['重视体验', '预算充足', '追求品质'],
    preferences: {
      activity_types: ['culture', 'leisure'],
      accommodation_level: 'premium',
      dining_style: ['western']
    },
    itinerary: {
      days: [
        {
          day: 1,
          date: '2025-05-10（周六）',
          items: [
            {
              time_start: '08:30',
              time_end: '09:00',
              activity: '公司集合，豪华大巴出发',
              location: '公司楼下'
            },
            {
              time_start: '09:00',
              time_end: '12:00',
              activity: '前往古北水镇',
              location: '豪华大巴'
            },
            {
              time_start: '12:00',
              time_end: '13:00',
              activity: '酒店check-in',
              location: '古北水镇精品酒店'
            },
            {
              time_start: '13:00',
              time_end: '14:30',
              activity: '午餐：精品餐厅',
              location: '酒店西餐厅'
            },
            {
              time_start: '14:30',
              time_end: '18:00',
              activity: '古镇文化体验 + 团队主题活动',
              location: '古北水镇景区'
            },
            {
              time_start: '18:00',
              time_end: '20:00',
              activity: '温泉SPA体验',
              location: '酒店温泉区'
            },
            {
              time_start: '20:00',
              time_end: '22:00',
              activity: '晚餐：高端团餐',
              location: '特色餐厅'
            },
            {
              time_start: '22:00',
              time_end: '',
              activity: '自由活动 / 休息',
              location: '酒店'
            }
          ]
        },
        {
          day: 2,
          date: '2025-05-11（周日）',
          items: [
            {
              time_start: '08:00',
              time_end: '09:30',
              activity: '早餐（自助餐）',
              location: '酒店餐厅'
            },
            {
              time_start: '09:30',
              time_end: '12:00',
              activity: '登长城 + 团队摄影',
              location: '司马台长城'
            },
            {
              time_start: '12:00',
              time_end: '13:30',
              activity: '午餐',
              location: '景区餐厅'
            },
            {
              time_start: '13:30',
              time_end: '16:30',
              activity: '返程',
              location: '豪华大巴'
            },
            {
              time_start: '16:30',
              time_end: '',
              activity: '到达公司，活动结束',
              location: '公司'
            }
          ]
        }
      ]
    },
    budget_breakdown: {
      categories: [
        {
          category: '交通',
          items: [
            { item: '豪华大巴往返', quantity: '1辆 x 2天', unit_price: 4000, total: 4000 }
          ],
          subtotal: 4000
        },
        {
          category: '住宿',
          items: [
            { item: '精品酒店（标间）', quantity: '25间 x 1晚', unit_price: 800, total: 20000 }
          ],
          subtotal: 20000
        },
        {
          category: '餐饮',
          items: [
            { item: '第一天午餐', quantity: '50人', unit_price: 120, total: 6000 },
            { item: '第一天晚餐', quantity: '50人', unit_price: 200, total: 10000 },
            { item: '第二天早餐', quantity: '50人', unit_price: 60, total: 3000 },
            { item: '第二天午餐', quantity: '50人', unit_price: 100, total: 5000 }
          ],
          subtotal: 24000
        },
        {
          category: '活动',
          items: [
            { item: '古镇门票', quantity: '50人', unit_price: 80, total: 4000 },
            { item: '温泉SPA', quantity: '50人', unit_price: 150, total: 7500 },
            { item: '长城门票', quantity: '50人', unit_price: 40, total: 2000 },
            { item: '专业摄影', quantity: '1天', unit_price: 2000, total: 2000 }
          ],
          subtotal: 15500
        },
        {
          category: '其他',
          items: [
            { item: '物料/保险/应急', quantity: '1批', unit_price: 2500, total: 2500 }
          ],
          subtotal: 2500
        }
      ],
      total: 66000,
      per_person: 1320
    },
    suppliers: [
      {
        supplier_id: 'sup_006',
        name: '古北水镇精品酒店',
        category: 'accommodation',
        rating: 4.9,
        price_range_min: 600,
        price_range_max: 1200,
        contact_phone: '13800138006',
        contact_wechat: 'gubei_hotel',
        tags: ['五星级', '温泉', '景区内']
      },
      {
        supplier_id: 'sup_007',
        name: '古北文化体验中心',
        category: 'activity',
        rating: 4.8,
        price_range_min: 80,
        price_range_max: 200,
        contact_phone: '13800138007',
        contact_wechat: 'gubei_culture',
        tags: ['文化体验', '专业导游', '定制服务']
      }
    ],
    created_at: '2025-01-02T10:30:00Z',
    generated_at: '2025-01-02T10:30:45Z'
  }
]

/**
 * 模拟用户信息
 */
export const mockUser = {
  user_id: 'user_mock_001',
  email: 'test@teamventure.com',
  name: '测试用户',
  company_name: '测试科技有限公司',
  company_size: 'medium',
  role: 'HR'
}

/**
 * 模拟登录响应
 */
export const mockLoginResponse = {
  sessionToken: 'mock_session_token_' + Date.now(),
  userInfo: mockUser
}
