-- ====================================
-- TeamVenture 供应商初始数据 V1.0.1
-- 创建日期: 2025-12-30
-- 说明: 北京地区供应商初始种子数据
-- 执行方式: source /path/to/V1.0.1__seed_suppliers.sql
-- ====================================

USE teamventure_main;

-- ====================================
-- 住宿类供应商 (accommodation)
-- ====================================
INSERT INTO suppliers (supplier_id, name, category, city, district, address,
                       contact_phone, contact_wechat, contact_person,
                       price_min, price_max, price_unit,
                       rating, review_count,
                       tags, capacity_min, capacity_max, status, verified)
VALUES
('sup_acc_001', '怀柔山水农家院', 'accommodation', '北京', '怀柔区', '怀柔镇雁栖湖北路88号',
 '13800138001', 'huairou_farmstay', '张老板',
 200, 500, 'per_room',
 4.5, 128,
 JSON_ARRAY('山景', '团建专供', '包场', '农家体验'), 20, 100, 'active', 1),

('sup_acc_002', '密云水库度假村', 'accommodation', '北京', '密云区', '密云区水库路188号',
 '13800138002', 'miyun_resort', '李经理',
 300, 800, 'per_room',
 4.8, 256,
 JSON_ARRAY('水景', '会议室', 'KTV', '垂钓'), 30, 150, 'active', 1),

('sup_acc_003', '延庆生态民宿', 'accommodation', '北京', '延庆区', '延庆区八达岭镇长城脚下',
 '13800138003', 'yanqing_bnb', '王女士',
 250, 600, 'per_room',
 4.6, 89,
 JSON_ARRAY('长城近邻', '生态环保', '观星'), 15, 80, 'active', 1),

('sup_acc_004', '平谷桃花源山庄', 'accommodation', '北京', '平谷区', '平谷区金海湖镇桃花路66号',
 '13800138004', 'pinggu_peach', '赵总',
 180, 450, 'per_room',
 4.4, 67,
 JSON_ARRAY('桃花主题', '果园采摘', '烧烤'), 20, 120, 'active', 1);

-- ====================================
-- 餐饮类供应商 (dining)
-- ====================================
INSERT INTO suppliers (supplier_id, name, category, city, district, address,
                       contact_phone, contact_wechat, contact_person,
                       price_min, price_max, price_unit,
                       rating, review_count,
                       tags, capacity_min, capacity_max, status, verified)
VALUES
('sup_din_001', '怀柔特色农家菜', 'dining', '北京', '怀柔区', '怀柔镇雁栖湖东路56号',
 '13800138011', 'huairou_food', '刘大厨',
 50, 100, 'per_person',
 4.3, 234,
 JSON_ARRAY('农家菜', '烤全羊', '柴鸡蛋', '虹鳟鱼'), 20, 200, 'active', 1),

('sup_din_002', '密云水库鱼宴', 'dining', '北京', '密云区', '密云区水库路98号',
 '13800138012', 'miyun_fish', '孙师傅',
 60, 120, 'per_person',
 4.7, 189,
 JSON_ARRAY('水库鱼', '湖鲜', '野菜', '有机'), 30, 300, 'active', 1),

('sup_din_003', '延庆火盆锅', 'dining', '北京', '延庆区', '延庆区八达岭镇古城街23号',
 '13800138013', 'yanqing_hotpot', '周老板',
 45, 90, 'per_person',
 4.5, 156,
 JSON_ARRAY('火盆锅', '延庆特色', '暖身', '冬季推荐'), 15, 150, 'active', 1),

('sup_din_004', '平谷农家宴', 'dining', '北京', '平谷区', '平谷区金海湖镇湖滨路12号',
 '13800138014', 'pinggu_feast', '吴师傅',
 40, 80, 'per_person',
 4.2, 98,
 JSON_ARRAY('平谷大桃', '农家菜', '柴火灶'), 20, 180, 'active', 1);

-- ====================================
-- 活动类供应商 (activity)
-- ====================================
INSERT INTO suppliers (supplier_id, name, category, city, district, address,
                       contact_phone, contact_wechat, contact_person,
                       price_min, price_max, price_unit,
                       rating, review_count,
                       tags, capacity_min, capacity_max, status, verified)
VALUES
('sup_act_001', '怀柔拓展训练基地', 'activity', '北京', '怀柔区', '怀柔区雁栖湖拓展中心',
 '13800138021', 'huairou_training', '马教练',
 100, 300, 'per_person',
 4.6, 345,
 JSON_ARRAY('户外拓展', '真人CS', '定向越野', '团队建设'), 30, 500, 'active', 1),

('sup_act_002', '密云水上运动中心', 'activity', '北京', '密云区', '密云区水库码头',
 '13800138022', 'miyun_water', '杨教练',
 120, 280, 'per_person',
 4.7, 267,
 JSON_ARRAY('皮划艇', '帆船', '龙舟', '水上拓展'), 25, 200, 'active', 1),

('sup_act_003', '延庆滑雪场', 'activity', '北京', '延庆区', '延庆区石京龙滑雪场',
 '13800138023', 'yanqing_ski', '冯教练',
 150, 400, 'per_person',
 4.8, 423,
 JSON_ARRAY('滑雪', '冬季团建', '教练指导', '初级友好'), 20, 300, 'active', 1),

('sup_act_004', '平谷采摘园', 'activity', '北京', '平谷区', '平谷区大华山镇桃园路88号',
 '13800138024', 'pinggu_picking', '田老板',
 50, 150, 'per_person',
 4.4, 178,
 JSON_ARRAY('果园采摘', '大桃', '春秋推荐', '亲近自然'), 15, 200, 'active', 1),

('sup_act_005', '怀柔真人CS基地', 'activity', '北京', '怀柔区', '怀柔区慕田峪长城附近',
 '13800138025', 'huairou_cs', '赵教练',
 80, 200, 'per_person',
 4.5, 289,
 JSON_ARRAY('真人CS', '战术对抗', '刺激', '团队协作'), 30, 400, 'active', 1);

-- ====================================
-- 交通类供应商 (transportation)
-- ====================================
INSERT INTO suppliers (supplier_id, name, category, city, district, address,
                       contact_phone, contact_wechat, contact_person,
                       price_min, price_max, price_unit,
                       rating, review_count,
                       tags, capacity_min, capacity_max, status, verified)
VALUES
('sup_tra_001', '北京旅游大巴公司', 'transportation', '北京', '朝阳区', '朝阳区东四环南路88号',
 '13800138031', 'bj_bus', '陈经理',
 4000, 8000, 'per_car',
 4.7, 456,
 JSON_ARRAY('正规车队', '保险齐全', '经验丰富', '37-55座'), 30, 500, 'active', 1),

('sup_tra_002', '京北包车服务', 'transportation', '北京', '海淀区', '海淀区中关村大街100号',
 '13800138032', 'jingbei_charter', '郑师傅',
 3500, 7000, 'per_car',
 4.6, 234,
 JSON_ARRAY('灵活调度', '商务车', '中小团队', '15-30座'), 15, 150, 'active', 1),

('sup_tra_003', '北京租车联盟', 'transportation', '北京', '丰台区', '丰台区南四环西路66号',
 '13800138033', 'bj_car_rental', '林经理',
 2500, 6000, 'per_car',
 4.5, 189,
 JSON_ARRAY('多车型', 'SUV车队', '自驾可选', '7-15座'), 7, 100, 'active', 1);

-- ====================================
-- 数据验证
-- ====================================
SELECT '✅ Supplier seed data inserted successfully!' AS status;
SELECT category, COUNT(*) AS count
FROM suppliers
WHERE status = 'active'
GROUP BY category;
