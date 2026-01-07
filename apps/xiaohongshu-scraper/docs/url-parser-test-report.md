# 小红书 URL 解析器测试报告

> 生成时间: 2026-01-05 21:56:06
>
> 测试样本: 1000 个
>
> 准确率: **100.00%**

## 目录

- [测试概要](#测试概要)
- [分类统计](#分类统计)
- [测试案例明细](#测试案例明细)
  - [explore 类型](#explore-类型)
  - [explore_with_params 类型](#explore_with_params-类型)
  - [discovery 类型](#discovery-类型)
  - [xhslink 类型](#xhslink-类型)
  - [xhslink_a 类型](#xhslink_a-类型)
  - [invalid_domain 类型](#invalid_domain-类型)
  - [invalid_format 类型](#invalid_format-类型)
  - [empty 类型](#empty-类型)
  - [malformed 类型](#malformed-类型)

## 测试概要

| 指标 | 数值 |
|------|------|
| 总测试数 | 1000 |
| 正确数 | 1000 |
| 错误数 | 0 |
| 准确率 | 100.00% |

## 分类统计

| URL类型 | 总数 | 正确 | 错误 | 准确率 |
|---------|------|------|------|--------|
| explore | 400 | 400 | 0 | 100.0% |
| explore_with_params | 150 | 150 | 0 | 100.0% |
| discovery | 100 | 100 | 0 | 100.0% |
| xhslink | 150 | 150 | 0 | 100.0% |
| xhslink_a | 100 | 100 | 0 | 100.0% |
| invalid_domain | 30 | 30 | 0 | 100.0% |
| invalid_format | 30 | 30 | 0 | 100.0% |
| empty | 20 | 20 | 0 | 100.0% |
| malformed | 20 | 20 | 0 | 100.0% |

## 测试案例明细

### explore 类型

> 标准 explore 页面格式，最常见的小红书笔记链接
>
> 共 400 个测试案例

| # | URL | 期望ID | 实际ID | 结果 |
|---|-----|--------|--------|------|
| 1 | `https://www.xiaohongshu.com/explore/cf3a5c35cb252c445129746e` | `cf3a5c35cb252c445129746e` | `cf3a5c35cb252c445129746e` | ✓ |
| 2 | `https://www.xiaohongshu.com/explore/4f663931f894dc497153f433` | `4f663931f894dc497153f433` | `4f663931f894dc497153f433` | ✓ |
| 3 | `https://www.xiaohongshu.com/explore/1e73512106596b1f78807080` | `1e73512106596b1f78807080` | `1e73512106596b1f78807080` | ✓ |
| 4 | `https://www.xiaohongshu.com/explore/0955e92bd2161132f2197d5a` | `0955e92bd2161132f2197d5a` | `0955e92bd2161132f2197d5a` | ✓ |
| 5 | `https://www.xiaohongshu.com/explore/47615a35c57330228ab209d9` | `47615a35c57330228ab209d9` | `47615a35c57330228ab209d9` | ✓ |
| 6 | `https://www.xiaohongshu.com/explore/90780e61decf732e77138d5a` | `90780e61decf732e77138d5a` | `90780e61decf732e77138d5a` | ✓ |
| 7 | `https://www.xiaohongshu.com/explore/8069011ae0aafe56f2270dd1` | `8069011ae0aafe56f2270dd1` | `8069011ae0aafe56f2270dd1` | ✓ |
| 8 | `https://www.xiaohongshu.com/explore/d1250cb868ad30ee85d6fe51` | `d1250cb868ad30ee85d6fe51` | `d1250cb868ad30ee85d6fe51` | ✓ |
| 9 | `https://www.xiaohongshu.com/explore/c56222eede18492c83c2ee86` | `c56222eede18492c83c2ee86` | `c56222eede18492c83c2ee86` | ✓ |
| 10 | `https://www.xiaohongshu.com/explore/90d38b065c751dbd0cbb2050` | `90d38b065c751dbd0cbb2050` | `90d38b065c751dbd0cbb2050` | ✓ |
| 11 | `https://www.xiaohongshu.com/explore/6251e29436341468297ed2cb` | `6251e29436341468297ed2cb` | `6251e29436341468297ed2cb` | ✓ |
| 12 | `https://www.xiaohongshu.com/explore/24284c08ecb3b86dc1222d6f` | `24284c08ecb3b86dc1222d6f` | `24284c08ecb3b86dc1222d6f` | ✓ |
| 13 | `https://www.xiaohongshu.com/explore/c32c43f8cc84e3055536866c` | `c32c43f8cc84e3055536866c` | `c32c43f8cc84e3055536866c` | ✓ |
| 14 | `https://www.xiaohongshu.com/explore/b5f6d691c4cf8c9b7567c8ec` | `b5f6d691c4cf8c9b7567c8ec` | `b5f6d691c4cf8c9b7567c8ec` | ✓ |
| 15 | `https://www.xiaohongshu.com/explore/ac4b4e3624ea6794310bee25` | `ac4b4e3624ea6794310bee25` | `ac4b4e3624ea6794310bee25` | ✓ |
| 16 | `https://www.xiaohongshu.com/explore/3fa435753d9c51806195722d` | `3fa435753d9c51806195722d` | `3fa435753d9c51806195722d` | ✓ |
| 17 | `https://www.xiaohongshu.com/explore/3acf71695cb3ef88750b1ae9` | `3acf71695cb3ef88750b1ae9` | `3acf71695cb3ef88750b1ae9` | ✓ |
| 18 | `https://www.xiaohongshu.com/explore/d0b7906d6cf2d382e972461a` | `d0b7906d6cf2d382e972461a` | `d0b7906d6cf2d382e972461a` | ✓ |
| 19 | `https://www.xiaohongshu.com/explore/f97e6cb51095bc8fd89c08d6` | `f97e6cb51095bc8fd89c08d6` | `f97e6cb51095bc8fd89c08d6` | ✓ |
| 20 | `https://www.xiaohongshu.com/explore/d88cf5392692bf759f05d06a` | `d88cf5392692bf759f05d06a` | `d88cf5392692bf759f05d06a` | ✓ |
| 21 | `https://www.xiaohongshu.com/explore/6c195fb47e63c2601538dc8b` | `6c195fb47e63c2601538dc8b` | `6c195fb47e63c2601538dc8b` | ✓ |
| 22 | `https://www.xiaohongshu.com/explore/482863ff69b7af6b60af7e2a` | `482863ff69b7af6b60af7e2a` | `482863ff69b7af6b60af7e2a` | ✓ |
| 23 | `https://www.xiaohongshu.com/explore/17c13c0f8afb7043b31ab429` | `17c13c0f8afb7043b31ab429` | `17c13c0f8afb7043b31ab429` | ✓ |
| 24 | `https://www.xiaohongshu.com/explore/a09bc561104bea331eac77db` | `a09bc561104bea331eac77db` | `a09bc561104bea331eac77db` | ✓ |
| 25 | `https://www.xiaohongshu.com/explore/1a53ba465f06067b72764830` | `1a53ba465f06067b72764830` | `1a53ba465f06067b72764830` | ✓ |
| 26 | `https://www.xiaohongshu.com/explore/785d5b1bffd59fa31110d925` | `785d5b1bffd59fa31110d925` | `785d5b1bffd59fa31110d925` | ✓ |
| 27 | `https://www.xiaohongshu.com/explore/a6fa3bfa95fd5fa91ea37cd8` | `a6fa3bfa95fd5fa91ea37cd8` | `a6fa3bfa95fd5fa91ea37cd8` | ✓ |
| 28 | `https://www.xiaohongshu.com/explore/4a27267adb8fe39fea70e858` | `4a27267adb8fe39fea70e858` | `4a27267adb8fe39fea70e858` | ✓ |
| 29 | `https://www.xiaohongshu.com/explore/289f4fe8e82a090ce44b5963` | `289f4fe8e82a090ce44b5963` | `289f4fe8e82a090ce44b5963` | ✓ |
| 30 | `https://www.xiaohongshu.com/explore/4342f2b3fbc415145479cd12` | `4342f2b3fbc415145479cd12` | `4342f2b3fbc415145479cd12` | ✓ |
| 31 | `https://www.xiaohongshu.com/explore/3d536af0d3aa47b73773cc9c` | `3d536af0d3aa47b73773cc9c` | `3d536af0d3aa47b73773cc9c` | ✓ |
| 32 | `https://www.xiaohongshu.com/explore/cf301ac80a05be6474127f2c` | `cf301ac80a05be6474127f2c` | `cf301ac80a05be6474127f2c` | ✓ |
| 33 | `https://www.xiaohongshu.com/explore/44965dbcc993404b4e860ab8` | `44965dbcc993404b4e860ab8` | `44965dbcc993404b4e860ab8` | ✓ |
| 34 | `https://www.xiaohongshu.com/explore/8eeb23a8c4b6244aec5c8ba6` | `8eeb23a8c4b6244aec5c8ba6` | `8eeb23a8c4b6244aec5c8ba6` | ✓ |
| 35 | `https://www.xiaohongshu.com/explore/6fe6192b23d023c04167bd6e` | `6fe6192b23d023c04167bd6e` | `6fe6192b23d023c04167bd6e` | ✓ |
| 36 | `https://www.xiaohongshu.com/explore/69d3eea466509a0358bf81cc` | `69d3eea466509a0358bf81cc` | `69d3eea466509a0358bf81cc` | ✓ |
| 37 | `https://www.xiaohongshu.com/explore/4afd3c1d76fb9b822571b3d0` | `4afd3c1d76fb9b822571b3d0` | `4afd3c1d76fb9b822571b3d0` | ✓ |
| 38 | `https://www.xiaohongshu.com/explore/979e75046ea31cf0dadb00e1` | `979e75046ea31cf0dadb00e1` | `979e75046ea31cf0dadb00e1` | ✓ |
| 39 | `https://www.xiaohongshu.com/explore/d961e30de8f5af005a1fae2d` | `d961e30de8f5af005a1fae2d` | `d961e30de8f5af005a1fae2d` | ✓ |
| 40 | `https://www.xiaohongshu.com/explore/35c16e0e490e29b787131d93` | `35c16e0e490e29b787131d93` | `35c16e0e490e29b787131d93` | ✓ |
| 41 | `https://www.xiaohongshu.com/explore/145f534d3d456ac46dbde5cc` | `145f534d3d456ac46dbde5cc` | `145f534d3d456ac46dbde5cc` | ✓ |
| 42 | `https://www.xiaohongshu.com/explore/b6c3019670f2786b46e4f05a` | `b6c3019670f2786b46e4f05a` | `b6c3019670f2786b46e4f05a` | ✓ |
| 43 | `https://www.xiaohongshu.com/explore/33f8fff2af2aaaf558685fbb` | `33f8fff2af2aaaf558685fbb` | `33f8fff2af2aaaf558685fbb` | ✓ |
| 44 | `https://www.xiaohongshu.com/explore/b5d4be16697c56f5de841fff` | `b5d4be16697c56f5de841fff` | `b5d4be16697c56f5de841fff` | ✓ |
| 45 | `https://www.xiaohongshu.com/explore/e09813966ff333ef55dd74f1` | `e09813966ff333ef55dd74f1` | `e09813966ff333ef55dd74f1` | ✓ |
| 46 | `https://www.xiaohongshu.com/explore/dd2a0bf272df96f7d5cf607d` | `dd2a0bf272df96f7d5cf607d` | `dd2a0bf272df96f7d5cf607d` | ✓ |
| 47 | `https://www.xiaohongshu.com/explore/2a9eee2806ff889f3acd7c90` | `2a9eee2806ff889f3acd7c90` | `2a9eee2806ff889f3acd7c90` | ✓ |
| 48 | `https://www.xiaohongshu.com/explore/723f498cf82bc9ed94e90454` | `723f498cf82bc9ed94e90454` | `723f498cf82bc9ed94e90454` | ✓ |
| 49 | `https://www.xiaohongshu.com/explore/8a4300bc68db88011caddac4` | `8a4300bc68db88011caddac4` | `8a4300bc68db88011caddac4` | ✓ |
| 50 | `https://www.xiaohongshu.com/explore/522c0f9d6561a81272a54639` | `522c0f9d6561a81272a54639` | `522c0f9d6561a81272a54639` | ✓ |
| 51 | `https://www.xiaohongshu.com/explore/84bd766027559aa941ad5660` | `84bd766027559aa941ad5660` | `84bd766027559aa941ad5660` | ✓ |
| 52 | `https://www.xiaohongshu.com/explore/fe9aec5520a573e508c409eb` | `fe9aec5520a573e508c409eb` | `fe9aec5520a573e508c409eb` | ✓ |
| 53 | `https://www.xiaohongshu.com/explore/df9b8c53ebe8d75fca67f0c9` | `df9b8c53ebe8d75fca67f0c9` | `df9b8c53ebe8d75fca67f0c9` | ✓ |
| 54 | `https://www.xiaohongshu.com/explore/0105d6b25f0070b275152b3f` | `0105d6b25f0070b275152b3f` | `0105d6b25f0070b275152b3f` | ✓ |
| 55 | `https://www.xiaohongshu.com/explore/4211aec60b8e5cd4e4b8835c` | `4211aec60b8e5cd4e4b8835c` | `4211aec60b8e5cd4e4b8835c` | ✓ |
| 56 | `https://www.xiaohongshu.com/explore/d263ee35504f04788302370c` | `d263ee35504f04788302370c` | `d263ee35504f04788302370c` | ✓ |
| 57 | `https://www.xiaohongshu.com/explore/553d1ab42f83462f21e03630` | `553d1ab42f83462f21e03630` | `553d1ab42f83462f21e03630` | ✓ |
| 58 | `https://www.xiaohongshu.com/explore/a4e27e2bc285f7ed0dd3a9b8` | `a4e27e2bc285f7ed0dd3a9b8` | `a4e27e2bc285f7ed0dd3a9b8` | ✓ |
| 59 | `https://www.xiaohongshu.com/explore/8ecc3a0167e44d6f00bc0fea` | `8ecc3a0167e44d6f00bc0fea` | `8ecc3a0167e44d6f00bc0fea` | ✓ |
| 60 | `https://www.xiaohongshu.com/explore/fcbfb37a24e19e04b40af3ae` | `fcbfb37a24e19e04b40af3ae` | `fcbfb37a24e19e04b40af3ae` | ✓ |
| 61 | `https://www.xiaohongshu.com/explore/56c6f97da5f35c514180ef74` | `56c6f97da5f35c514180ef74` | `56c6f97da5f35c514180ef74` | ✓ |
| 62 | `https://www.xiaohongshu.com/explore/151391d1f6f13b6491a229c7` | `151391d1f6f13b6491a229c7` | `151391d1f6f13b6491a229c7` | ✓ |
| 63 | `https://www.xiaohongshu.com/explore/899edfb023b68ce3a6c54788` | `899edfb023b68ce3a6c54788` | `899edfb023b68ce3a6c54788` | ✓ |
| 64 | `https://www.xiaohongshu.com/explore/90fed94e052dbe08895e5399` | `90fed94e052dbe08895e5399` | `90fed94e052dbe08895e5399` | ✓ |
| 65 | `https://www.xiaohongshu.com/explore/a3582a40b88263fc73b7f4f6` | `a3582a40b88263fc73b7f4f6` | `a3582a40b88263fc73b7f4f6` | ✓ |
| 66 | `https://www.xiaohongshu.com/explore/648744f322bc9e62d8127de3` | `648744f322bc9e62d8127de3` | `648744f322bc9e62d8127de3` | ✓ |
| 67 | `https://www.xiaohongshu.com/explore/94b955035851a19239c359c5` | `94b955035851a19239c359c5` | `94b955035851a19239c359c5` | ✓ |
| 68 | `https://www.xiaohongshu.com/explore/c6fc45b0d47285a4387be06d` | `c6fc45b0d47285a4387be06d` | `c6fc45b0d47285a4387be06d` | ✓ |
| 69 | `https://www.xiaohongshu.com/explore/11ccf1dd401bd3a67cd29c49` | `11ccf1dd401bd3a67cd29c49` | `11ccf1dd401bd3a67cd29c49` | ✓ |
| 70 | `https://www.xiaohongshu.com/explore/66a14e0b19f4433bf90d2317` | `66a14e0b19f4433bf90d2317` | `66a14e0b19f4433bf90d2317` | ✓ |
| 71 | `https://www.xiaohongshu.com/explore/709a0816b049ff919c3064b0` | `709a0816b049ff919c3064b0` | `709a0816b049ff919c3064b0` | ✓ |
| 72 | `https://www.xiaohongshu.com/explore/f452f819d2e380f5e33af36b` | `f452f819d2e380f5e33af36b` | `f452f819d2e380f5e33af36b` | ✓ |
| 73 | `https://www.xiaohongshu.com/explore/8bfa2c3684a57f1cff1e55d2` | `8bfa2c3684a57f1cff1e55d2` | `8bfa2c3684a57f1cff1e55d2` | ✓ |
| 74 | `https://www.xiaohongshu.com/explore/637ac8cd6fd45c7c5aeff245` | `637ac8cd6fd45c7c5aeff245` | `637ac8cd6fd45c7c5aeff245` | ✓ |
| 75 | `https://www.xiaohongshu.com/explore/a48a2805b3901e4648170fe8` | `a48a2805b3901e4648170fe8` | `a48a2805b3901e4648170fe8` | ✓ |
| 76 | `https://www.xiaohongshu.com/explore/914cb6e154f4ef7814878a33` | `914cb6e154f4ef7814878a33` | `914cb6e154f4ef7814878a33` | ✓ |
| 77 | `https://www.xiaohongshu.com/explore/82ae2c4626cc409b89bac9e6` | `82ae2c4626cc409b89bac9e6` | `82ae2c4626cc409b89bac9e6` | ✓ |
| 78 | `https://www.xiaohongshu.com/explore/e212d752ed8223d49abb41af` | `e212d752ed8223d49abb41af` | `e212d752ed8223d49abb41af` | ✓ |
| 79 | `https://www.xiaohongshu.com/explore/d2506453e4ce2131e9abf2d3` | `d2506453e4ce2131e9abf2d3` | `d2506453e4ce2131e9abf2d3` | ✓ |
| 80 | `https://www.xiaohongshu.com/explore/134ee28859a41dad497357f9` | `134ee28859a41dad497357f9` | `134ee28859a41dad497357f9` | ✓ |
| 81 | `https://www.xiaohongshu.com/explore/a57c2ab088153787bc12e6a3` | `a57c2ab088153787bc12e6a3` | `a57c2ab088153787bc12e6a3` | ✓ |
| 82 | `https://www.xiaohongshu.com/explore/997024fb9da76818e2c57104` | `997024fb9da76818e2c57104` | `997024fb9da76818e2c57104` | ✓ |
| 83 | `https://www.xiaohongshu.com/explore/1d8006f6c1248f66759cb15d` | `1d8006f6c1248f66759cb15d` | `1d8006f6c1248f66759cb15d` | ✓ |
| 84 | `https://www.xiaohongshu.com/explore/04d0959b3b8adc5d21d0fe4f` | `04d0959b3b8adc5d21d0fe4f` | `04d0959b3b8adc5d21d0fe4f` | ✓ |
| 85 | `https://www.xiaohongshu.com/explore/866a53884c6e68f896c1c9e2` | `866a53884c6e68f896c1c9e2` | `866a53884c6e68f896c1c9e2` | ✓ |
| 86 | `https://www.xiaohongshu.com/explore/47363f8ba5858f1af6bd4dca` | `47363f8ba5858f1af6bd4dca` | `47363f8ba5858f1af6bd4dca` | ✓ |
| 87 | `https://www.xiaohongshu.com/explore/97ba3e4d085d5fea3d3c25ed` | `97ba3e4d085d5fea3d3c25ed` | `97ba3e4d085d5fea3d3c25ed` | ✓ |
| 88 | `https://www.xiaohongshu.com/explore/5193b1f20eb7d6d0231d0022` | `5193b1f20eb7d6d0231d0022` | `5193b1f20eb7d6d0231d0022` | ✓ |
| 89 | `https://www.xiaohongshu.com/explore/54eff328a932792adf866f52` | `54eff328a932792adf866f52` | `54eff328a932792adf866f52` | ✓ |
| 90 | `https://www.xiaohongshu.com/explore/7a7f656247df79471d923e1d` | `7a7f656247df79471d923e1d` | `7a7f656247df79471d923e1d` | ✓ |
| 91 | `https://www.xiaohongshu.com/explore/76e1673d0b31cccfc5d5af17` | `76e1673d0b31cccfc5d5af17` | `76e1673d0b31cccfc5d5af17` | ✓ |
| 92 | `https://www.xiaohongshu.com/explore/70adc7b4cbe5416bbf2eaf8c` | `70adc7b4cbe5416bbf2eaf8c` | `70adc7b4cbe5416bbf2eaf8c` | ✓ |
| 93 | `https://www.xiaohongshu.com/explore/f3d7de16801f210b432c7825` | `f3d7de16801f210b432c7825` | `f3d7de16801f210b432c7825` | ✓ |
| 94 | `https://www.xiaohongshu.com/explore/0bbb03ea23b3dd1c4bcf0eb5` | `0bbb03ea23b3dd1c4bcf0eb5` | `0bbb03ea23b3dd1c4bcf0eb5` | ✓ |
| 95 | `https://www.xiaohongshu.com/explore/33aed5152c2862931a8c8a37` | `33aed5152c2862931a8c8a37` | `33aed5152c2862931a8c8a37` | ✓ |
| 96 | `https://www.xiaohongshu.com/explore/2b47d1a694ad38189b40e49a` | `2b47d1a694ad38189b40e49a` | `2b47d1a694ad38189b40e49a` | ✓ |
| 97 | `https://www.xiaohongshu.com/explore/cbfa55c6ebbce99cf454ffbb` | `cbfa55c6ebbce99cf454ffbb` | `cbfa55c6ebbce99cf454ffbb` | ✓ |
| 98 | `https://www.xiaohongshu.com/explore/f151bcdc00fdb23d75b48fbb` | `f151bcdc00fdb23d75b48fbb` | `f151bcdc00fdb23d75b48fbb` | ✓ |
| 99 | `https://www.xiaohongshu.com/explore/2bcbf446baf5754d2819cde8` | `2bcbf446baf5754d2819cde8` | `2bcbf446baf5754d2819cde8` | ✓ |
| 100 | `https://www.xiaohongshu.com/explore/6d6ef5349678f22f1b9758c6` | `6d6ef5349678f22f1b9758c6` | `6d6ef5349678f22f1b9758c6` | ✓ |
| 101 | `https://www.xiaohongshu.com/explore/417ac463f222d7878984ae99` | `417ac463f222d7878984ae99` | `417ac463f222d7878984ae99` | ✓ |
| 102 | `https://www.xiaohongshu.com/explore/03905e50b1334cf0d7a135b8` | `03905e50b1334cf0d7a135b8` | `03905e50b1334cf0d7a135b8` | ✓ |
| 103 | `https://www.xiaohongshu.com/explore/6ad44dd3fd987caaae024097` | `6ad44dd3fd987caaae024097` | `6ad44dd3fd987caaae024097` | ✓ |
| 104 | `https://www.xiaohongshu.com/explore/e8ea74cd0b187cbf37d78668` | `e8ea74cd0b187cbf37d78668` | `e8ea74cd0b187cbf37d78668` | ✓ |
| 105 | `https://www.xiaohongshu.com/explore/528571449e9047c881ae8346` | `528571449e9047c881ae8346` | `528571449e9047c881ae8346` | ✓ |
| 106 | `https://www.xiaohongshu.com/explore/51d1c968628f376d0d687b6a` | `51d1c968628f376d0d687b6a` | `51d1c968628f376d0d687b6a` | ✓ |
| 107 | `https://www.xiaohongshu.com/explore/ceaba40d3114344e55a433ff` | `ceaba40d3114344e55a433ff` | `ceaba40d3114344e55a433ff` | ✓ |
| 108 | `https://www.xiaohongshu.com/explore/67f2d2117fc93ffc47a2a112` | `67f2d2117fc93ffc47a2a112` | `67f2d2117fc93ffc47a2a112` | ✓ |
| 109 | `https://www.xiaohongshu.com/explore/467442a5813fde45491cbf03` | `467442a5813fde45491cbf03` | `467442a5813fde45491cbf03` | ✓ |
| 110 | `https://www.xiaohongshu.com/explore/5bf34ffecb34c29b941b8017` | `5bf34ffecb34c29b941b8017` | `5bf34ffecb34c29b941b8017` | ✓ |
| 111 | `https://www.xiaohongshu.com/explore/e0ee141509d061645a4ee041` | `e0ee141509d061645a4ee041` | `e0ee141509d061645a4ee041` | ✓ |
| 112 | `https://www.xiaohongshu.com/explore/5eb322121e480e733541872d` | `5eb322121e480e733541872d` | `5eb322121e480e733541872d` | ✓ |
| 113 | `https://www.xiaohongshu.com/explore/aff23cb6647e7bbc4e3b7253` | `aff23cb6647e7bbc4e3b7253` | `aff23cb6647e7bbc4e3b7253` | ✓ |
| 114 | `https://www.xiaohongshu.com/explore/7b1c65ce20d2b98365a24e88` | `7b1c65ce20d2b98365a24e88` | `7b1c65ce20d2b98365a24e88` | ✓ |
| 115 | `https://www.xiaohongshu.com/explore/c62756994d62772059583763` | `c62756994d62772059583763` | `c62756994d62772059583763` | ✓ |
| 116 | `https://www.xiaohongshu.com/explore/4ab3078cd8bf659d576e3b88` | `4ab3078cd8bf659d576e3b88` | `4ab3078cd8bf659d576e3b88` | ✓ |
| 117 | `https://www.xiaohongshu.com/explore/11ff8f5b7b102f8432623f3a` | `11ff8f5b7b102f8432623f3a` | `11ff8f5b7b102f8432623f3a` | ✓ |
| 118 | `https://www.xiaohongshu.com/explore/a1475dd0f1adefbe34d44109` | `a1475dd0f1adefbe34d44109` | `a1475dd0f1adefbe34d44109` | ✓ |
| 119 | `https://www.xiaohongshu.com/explore/8ce8619a829f02aae18cc69e` | `8ce8619a829f02aae18cc69e` | `8ce8619a829f02aae18cc69e` | ✓ |
| 120 | `https://www.xiaohongshu.com/explore/ea99b2460b7afea33dc1bc68` | `ea99b2460b7afea33dc1bc68` | `ea99b2460b7afea33dc1bc68` | ✓ |
| 121 | `https://www.xiaohongshu.com/explore/e9d8fe2737fefb6942a3feec` | `e9d8fe2737fefb6942a3feec` | `e9d8fe2737fefb6942a3feec` | ✓ |
| 122 | `https://www.xiaohongshu.com/explore/82444f5b8045d16019e1a489` | `82444f5b8045d16019e1a489` | `82444f5b8045d16019e1a489` | ✓ |
| 123 | `https://www.xiaohongshu.com/explore/709759749db148292663e560` | `709759749db148292663e560` | `709759749db148292663e560` | ✓ |
| 124 | `https://www.xiaohongshu.com/explore/014f01f9944bedf791138569` | `014f01f9944bedf791138569` | `014f01f9944bedf791138569` | ✓ |
| 125 | `https://www.xiaohongshu.com/explore/f957c09071d6914b86d6b7e0` | `f957c09071d6914b86d6b7e0` | `f957c09071d6914b86d6b7e0` | ✓ |
| 126 | `https://www.xiaohongshu.com/explore/f6dc750e2d8729c2d374f61a` | `f6dc750e2d8729c2d374f61a` | `f6dc750e2d8729c2d374f61a` | ✓ |
| 127 | `https://www.xiaohongshu.com/explore/2b938e33937ff697a824a12c` | `2b938e33937ff697a824a12c` | `2b938e33937ff697a824a12c` | ✓ |
| 128 | `https://www.xiaohongshu.com/explore/a1bae2cc62e63c2f24c03e9a` | `a1bae2cc62e63c2f24c03e9a` | `a1bae2cc62e63c2f24c03e9a` | ✓ |
| 129 | `https://www.xiaohongshu.com/explore/5d82814746b948045f6332ab` | `5d82814746b948045f6332ab` | `5d82814746b948045f6332ab` | ✓ |
| 130 | `https://www.xiaohongshu.com/explore/1ab78416e20285f4fdc0091a` | `1ab78416e20285f4fdc0091a` | `1ab78416e20285f4fdc0091a` | ✓ |
| 131 | `https://www.xiaohongshu.com/explore/b50f3b87a46635b20afbe7b7` | `b50f3b87a46635b20afbe7b7` | `b50f3b87a46635b20afbe7b7` | ✓ |
| 132 | `https://www.xiaohongshu.com/explore/2c9888c1a521d4698caecda1` | `2c9888c1a521d4698caecda1` | `2c9888c1a521d4698caecda1` | ✓ |
| 133 | `https://www.xiaohongshu.com/explore/71fd1e3585b8d4ed21d6eb93` | `71fd1e3585b8d4ed21d6eb93` | `71fd1e3585b8d4ed21d6eb93` | ✓ |
| 134 | `https://www.xiaohongshu.com/explore/2fe939bfd8efeda136fb7013` | `2fe939bfd8efeda136fb7013` | `2fe939bfd8efeda136fb7013` | ✓ |
| 135 | `https://www.xiaohongshu.com/explore/22c4d148848225e8a3e31b55` | `22c4d148848225e8a3e31b55` | `22c4d148848225e8a3e31b55` | ✓ |
| 136 | `https://www.xiaohongshu.com/explore/1a285c48756e6f5cc8322b10` | `1a285c48756e6f5cc8322b10` | `1a285c48756e6f5cc8322b10` | ✓ |
| 137 | `https://www.xiaohongshu.com/explore/5d4b9a35eca12f4a463739de` | `5d4b9a35eca12f4a463739de` | `5d4b9a35eca12f4a463739de` | ✓ |
| 138 | `https://www.xiaohongshu.com/explore/7b5ea109a90f27abeae1019d` | `7b5ea109a90f27abeae1019d` | `7b5ea109a90f27abeae1019d` | ✓ |
| 139 | `https://www.xiaohongshu.com/explore/09737a8886a51e848bb9eea8` | `09737a8886a51e848bb9eea8` | `09737a8886a51e848bb9eea8` | ✓ |
| 140 | `https://www.xiaohongshu.com/explore/ced93a2a375bb1fb67f51961` | `ced93a2a375bb1fb67f51961` | `ced93a2a375bb1fb67f51961` | ✓ |
| 141 | `https://www.xiaohongshu.com/explore/ce917abeda867c2aa21e5976` | `ce917abeda867c2aa21e5976` | `ce917abeda867c2aa21e5976` | ✓ |
| 142 | `https://www.xiaohongshu.com/explore/4a39260dcd09196669265ccb` | `4a39260dcd09196669265ccb` | `4a39260dcd09196669265ccb` | ✓ |
| 143 | `https://www.xiaohongshu.com/explore/0abb16d13d3ec060af991ba7` | `0abb16d13d3ec060af991ba7` | `0abb16d13d3ec060af991ba7` | ✓ |
| 144 | `https://www.xiaohongshu.com/explore/fbaf260e03521c2a5d683af1` | `fbaf260e03521c2a5d683af1` | `fbaf260e03521c2a5d683af1` | ✓ |
| 145 | `https://www.xiaohongshu.com/explore/b8490ef2d148fb4da61ea4e8` | `b8490ef2d148fb4da61ea4e8` | `b8490ef2d148fb4da61ea4e8` | ✓ |
| 146 | `https://www.xiaohongshu.com/explore/eed4cc55b0d337f7612b6228` | `eed4cc55b0d337f7612b6228` | `eed4cc55b0d337f7612b6228` | ✓ |
| 147 | `https://www.xiaohongshu.com/explore/072c38ef5fb93d39dfb8cd1e` | `072c38ef5fb93d39dfb8cd1e` | `072c38ef5fb93d39dfb8cd1e` | ✓ |
| 148 | `https://www.xiaohongshu.com/explore/2d5d71adcdedb17645fa4372` | `2d5d71adcdedb17645fa4372` | `2d5d71adcdedb17645fa4372` | ✓ |
| 149 | `https://www.xiaohongshu.com/explore/77a145f61a91fe1f6306a5ee` | `77a145f61a91fe1f6306a5ee` | `77a145f61a91fe1f6306a5ee` | ✓ |
| 150 | `https://www.xiaohongshu.com/explore/16066b4849694cf2cdb94ec2` | `16066b4849694cf2cdb94ec2` | `16066b4849694cf2cdb94ec2` | ✓ |
| 151 | `https://www.xiaohongshu.com/explore/9060ff0a50c9864c31d8aace` | `9060ff0a50c9864c31d8aace` | `9060ff0a50c9864c31d8aace` | ✓ |
| 152 | `https://www.xiaohongshu.com/explore/80181589c699b1e6a6ebc94e` | `80181589c699b1e6a6ebc94e` | `80181589c699b1e6a6ebc94e` | ✓ |
| 153 | `https://www.xiaohongshu.com/explore/b45eababbe0036a46c21e90f` | `b45eababbe0036a46c21e90f` | `b45eababbe0036a46c21e90f` | ✓ |
| 154 | `https://www.xiaohongshu.com/explore/d43bbff360eeb8c835bc2853` | `d43bbff360eeb8c835bc2853` | `d43bbff360eeb8c835bc2853` | ✓ |
| 155 | `https://www.xiaohongshu.com/explore/3d430c3820ce54a11650c7c8` | `3d430c3820ce54a11650c7c8` | `3d430c3820ce54a11650c7c8` | ✓ |
| 156 | `https://www.xiaohongshu.com/explore/1d6eb0b7cf317f5cf5e70685` | `1d6eb0b7cf317f5cf5e70685` | `1d6eb0b7cf317f5cf5e70685` | ✓ |
| 157 | `https://www.xiaohongshu.com/explore/a50bb3b0f26823b8abf9ea27` | `a50bb3b0f26823b8abf9ea27` | `a50bb3b0f26823b8abf9ea27` | ✓ |
| 158 | `https://www.xiaohongshu.com/explore/7db8176e2c5e93e3cc0d0327` | `7db8176e2c5e93e3cc0d0327` | `7db8176e2c5e93e3cc0d0327` | ✓ |
| 159 | `https://www.xiaohongshu.com/explore/27ea8304842713fb8cd03775` | `27ea8304842713fb8cd03775` | `27ea8304842713fb8cd03775` | ✓ |
| 160 | `https://www.xiaohongshu.com/explore/e9f29a8375776610f9269b99` | `e9f29a8375776610f9269b99` | `e9f29a8375776610f9269b99` | ✓ |
| 161 | `https://www.xiaohongshu.com/explore/52eab3bba13c2c3085c18d6a` | `52eab3bba13c2c3085c18d6a` | `52eab3bba13c2c3085c18d6a` | ✓ |
| 162 | `https://www.xiaohongshu.com/explore/9fd7831303f6f5f19b7fca65` | `9fd7831303f6f5f19b7fca65` | `9fd7831303f6f5f19b7fca65` | ✓ |
| 163 | `https://www.xiaohongshu.com/explore/093101a33efddf664347d963` | `093101a33efddf664347d963` | `093101a33efddf664347d963` | ✓ |
| 164 | `https://www.xiaohongshu.com/explore/03666403260dd382570d2c4a` | `03666403260dd382570d2c4a` | `03666403260dd382570d2c4a` | ✓ |
| 165 | `https://www.xiaohongshu.com/explore/80541f000adc019c68933596` | `80541f000adc019c68933596` | `80541f000adc019c68933596` | ✓ |
| 166 | `https://www.xiaohongshu.com/explore/2432dae71b34d349a6cec0d8` | `2432dae71b34d349a6cec0d8` | `2432dae71b34d349a6cec0d8` | ✓ |
| 167 | `https://www.xiaohongshu.com/explore/a367bb96e71636151960fdfd` | `a367bb96e71636151960fdfd` | `a367bb96e71636151960fdfd` | ✓ |
| 168 | `https://www.xiaohongshu.com/explore/ff12b015b173771e951740f0` | `ff12b015b173771e951740f0` | `ff12b015b173771e951740f0` | ✓ |
| 169 | `https://www.xiaohongshu.com/explore/509eb473b7e31d7fc92b7afb` | `509eb473b7e31d7fc92b7afb` | `509eb473b7e31d7fc92b7afb` | ✓ |
| 170 | `https://www.xiaohongshu.com/explore/d9d2808274186dc64601614a` | `d9d2808274186dc64601614a` | `d9d2808274186dc64601614a` | ✓ |
| 171 | `https://www.xiaohongshu.com/explore/46937705053c2877cdcff0df` | `46937705053c2877cdcff0df` | `46937705053c2877cdcff0df` | ✓ |
| 172 | `https://www.xiaohongshu.com/explore/6be88abd59fcdf97ac6983fc` | `6be88abd59fcdf97ac6983fc` | `6be88abd59fcdf97ac6983fc` | ✓ |
| 173 | `https://www.xiaohongshu.com/explore/5664585057cd5345935489be` | `5664585057cd5345935489be` | `5664585057cd5345935489be` | ✓ |
| 174 | `https://www.xiaohongshu.com/explore/8f09e194ddef168c553510de` | `8f09e194ddef168c553510de` | `8f09e194ddef168c553510de` | ✓ |
| 175 | `https://www.xiaohongshu.com/explore/83c413115a658163f9b72430` | `83c413115a658163f9b72430` | `83c413115a658163f9b72430` | ✓ |
| 176 | `https://www.xiaohongshu.com/explore/68f074ae23e3f2c52f229525` | `68f074ae23e3f2c52f229525` | `68f074ae23e3f2c52f229525` | ✓ |
| 177 | `https://www.xiaohongshu.com/explore/e561fa06e4d56e20f8f4c997` | `e561fa06e4d56e20f8f4c997` | `e561fa06e4d56e20f8f4c997` | ✓ |
| 178 | `https://www.xiaohongshu.com/explore/afb821fe70b19c0a44181dab` | `afb821fe70b19c0a44181dab` | `afb821fe70b19c0a44181dab` | ✓ |
| 179 | `https://www.xiaohongshu.com/explore/ac1f86cf748183ee30f9bcc6` | `ac1f86cf748183ee30f9bcc6` | `ac1f86cf748183ee30f9bcc6` | ✓ |
| 180 | `https://www.xiaohongshu.com/explore/864417d948773145d1a90a25` | `864417d948773145d1a90a25` | `864417d948773145d1a90a25` | ✓ |
| 181 | `https://www.xiaohongshu.com/explore/9fea3e8de74b9d3f2d7cf78e` | `9fea3e8de74b9d3f2d7cf78e` | `9fea3e8de74b9d3f2d7cf78e` | ✓ |
| 182 | `https://www.xiaohongshu.com/explore/92d209128c914c1db0cfc369` | `92d209128c914c1db0cfc369` | `92d209128c914c1db0cfc369` | ✓ |
| 183 | `https://www.xiaohongshu.com/explore/4c65affa9aa9615a3ca98702` | `4c65affa9aa9615a3ca98702` | `4c65affa9aa9615a3ca98702` | ✓ |
| 184 | `https://www.xiaohongshu.com/explore/a308f84ec163238b424ad394` | `a308f84ec163238b424ad394` | `a308f84ec163238b424ad394` | ✓ |
| 185 | `https://www.xiaohongshu.com/explore/edee4840e52769ecc8542fce` | `edee4840e52769ecc8542fce` | `edee4840e52769ecc8542fce` | ✓ |
| 186 | `https://www.xiaohongshu.com/explore/00b05a8860cc147babc5846b` | `00b05a8860cc147babc5846b` | `00b05a8860cc147babc5846b` | ✓ |
| 187 | `https://www.xiaohongshu.com/explore/ea014cc34f923f328581d0dc` | `ea014cc34f923f328581d0dc` | `ea014cc34f923f328581d0dc` | ✓ |
| 188 | `https://www.xiaohongshu.com/explore/f63fc736d8b47c0027af0615` | `f63fc736d8b47c0027af0615` | `f63fc736d8b47c0027af0615` | ✓ |
| 189 | `https://www.xiaohongshu.com/explore/dda08ac4db63eeae6a7695a7` | `dda08ac4db63eeae6a7695a7` | `dda08ac4db63eeae6a7695a7` | ✓ |
| 190 | `https://www.xiaohongshu.com/explore/1f8c1641be98c404992432f8` | `1f8c1641be98c404992432f8` | `1f8c1641be98c404992432f8` | ✓ |
| 191 | `https://www.xiaohongshu.com/explore/08dc87056fbd6b47d5590239` | `08dc87056fbd6b47d5590239` | `08dc87056fbd6b47d5590239` | ✓ |
| 192 | `https://www.xiaohongshu.com/explore/9a151b6b89341ace76956522` | `9a151b6b89341ace76956522` | `9a151b6b89341ace76956522` | ✓ |
| 193 | `https://www.xiaohongshu.com/explore/8adc6b2f619c2cab8ce0bab2` | `8adc6b2f619c2cab8ce0bab2` | `8adc6b2f619c2cab8ce0bab2` | ✓ |
| 194 | `https://www.xiaohongshu.com/explore/2b0f412f2ef3f8689e3b2bdd` | `2b0f412f2ef3f8689e3b2bdd` | `2b0f412f2ef3f8689e3b2bdd` | ✓ |
| 195 | `https://www.xiaohongshu.com/explore/45672f1d4d93f2910334cd0e` | `45672f1d4d93f2910334cd0e` | `45672f1d4d93f2910334cd0e` | ✓ |
| 196 | `https://www.xiaohongshu.com/explore/9535ce241ba202b642c1a041` | `9535ce241ba202b642c1a041` | `9535ce241ba202b642c1a041` | ✓ |
| 197 | `https://www.xiaohongshu.com/explore/e9fe214f30b5f2be1ad4dead` | `e9fe214f30b5f2be1ad4dead` | `e9fe214f30b5f2be1ad4dead` | ✓ |
| 198 | `https://www.xiaohongshu.com/explore/8a1e9840e3e35e77d7d91bf7` | `8a1e9840e3e35e77d7d91bf7` | `8a1e9840e3e35e77d7d91bf7` | ✓ |
| 199 | `https://www.xiaohongshu.com/explore/f3093377ab45721e2a3863e0` | `f3093377ab45721e2a3863e0` | `f3093377ab45721e2a3863e0` | ✓ |
| 200 | `https://www.xiaohongshu.com/explore/3fd491a8c82a2dc52d47893e` | `3fd491a8c82a2dc52d47893e` | `3fd491a8c82a2dc52d47893e` | ✓ |
| 201 | `https://www.xiaohongshu.com/explore/83865479f8163a43a71e3f5b` | `83865479f8163a43a71e3f5b` | `83865479f8163a43a71e3f5b` | ✓ |
| 202 | `https://www.xiaohongshu.com/explore/3265528e044ac8e1e982c6a6` | `3265528e044ac8e1e982c6a6` | `3265528e044ac8e1e982c6a6` | ✓ |
| 203 | `https://www.xiaohongshu.com/explore/170e5eb54e9b7185281bdf7e` | `170e5eb54e9b7185281bdf7e` | `170e5eb54e9b7185281bdf7e` | ✓ |
| 204 | `https://www.xiaohongshu.com/explore/a4a293a544e4761155d998e8` | `a4a293a544e4761155d998e8` | `a4a293a544e4761155d998e8` | ✓ |
| 205 | `https://www.xiaohongshu.com/explore/4646b40a97706bfea5aebfe9` | `4646b40a97706bfea5aebfe9` | `4646b40a97706bfea5aebfe9` | ✓ |
| 206 | `https://www.xiaohongshu.com/explore/99c06690d35328477c52dca3` | `99c06690d35328477c52dca3` | `99c06690d35328477c52dca3` | ✓ |
| 207 | `https://www.xiaohongshu.com/explore/3389be6b8d65547205049dac` | `3389be6b8d65547205049dac` | `3389be6b8d65547205049dac` | ✓ |
| 208 | `https://www.xiaohongshu.com/explore/3c3718e238a47bf8d7f4b962` | `3c3718e238a47bf8d7f4b962` | `3c3718e238a47bf8d7f4b962` | ✓ |
| 209 | `https://www.xiaohongshu.com/explore/e63ea50a3531af24c391d961` | `e63ea50a3531af24c391d961` | `e63ea50a3531af24c391d961` | ✓ |
| 210 | `https://www.xiaohongshu.com/explore/571d7de3cf21a63be5da164c` | `571d7de3cf21a63be5da164c` | `571d7de3cf21a63be5da164c` | ✓ |
| 211 | `https://www.xiaohongshu.com/explore/1d01d2320e6a2085f4fc8ddd` | `1d01d2320e6a2085f4fc8ddd` | `1d01d2320e6a2085f4fc8ddd` | ✓ |
| 212 | `https://www.xiaohongshu.com/explore/65bc198d739c4d4d4476a488` | `65bc198d739c4d4d4476a488` | `65bc198d739c4d4d4476a488` | ✓ |
| 213 | `https://www.xiaohongshu.com/explore/3dfec20a451a5d1f73a26a80` | `3dfec20a451a5d1f73a26a80` | `3dfec20a451a5d1f73a26a80` | ✓ |
| 214 | `https://www.xiaohongshu.com/explore/fe38e8f78d1149408060acbf` | `fe38e8f78d1149408060acbf` | `fe38e8f78d1149408060acbf` | ✓ |
| 215 | `https://www.xiaohongshu.com/explore/18ab822d2fc53d2ba47cf8f6` | `18ab822d2fc53d2ba47cf8f6` | `18ab822d2fc53d2ba47cf8f6` | ✓ |
| 216 | `https://www.xiaohongshu.com/explore/06c30d8c1c5c3bce12c3413b` | `06c30d8c1c5c3bce12c3413b` | `06c30d8c1c5c3bce12c3413b` | ✓ |
| 217 | `https://www.xiaohongshu.com/explore/f9ecf811865dbc10ac17f2dc` | `f9ecf811865dbc10ac17f2dc` | `f9ecf811865dbc10ac17f2dc` | ✓ |
| 218 | `https://www.xiaohongshu.com/explore/e04e962fe00844cf3343fc2e` | `e04e962fe00844cf3343fc2e` | `e04e962fe00844cf3343fc2e` | ✓ |
| 219 | `https://www.xiaohongshu.com/explore/9fda6df2d1dfd610606137eb` | `9fda6df2d1dfd610606137eb` | `9fda6df2d1dfd610606137eb` | ✓ |
| 220 | `https://www.xiaohongshu.com/explore/7786da01891d8c2c9a269b13` | `7786da01891d8c2c9a269b13` | `7786da01891d8c2c9a269b13` | ✓ |
| 221 | `https://www.xiaohongshu.com/explore/41f1106280c2eeb066366cbf` | `41f1106280c2eeb066366cbf` | `41f1106280c2eeb066366cbf` | ✓ |
| 222 | `https://www.xiaohongshu.com/explore/6b8ffb640c389c6b5e613d41` | `6b8ffb640c389c6b5e613d41` | `6b8ffb640c389c6b5e613d41` | ✓ |
| 223 | `https://www.xiaohongshu.com/explore/830d5f1b0e07c9bb9bf7e54d` | `830d5f1b0e07c9bb9bf7e54d` | `830d5f1b0e07c9bb9bf7e54d` | ✓ |
| 224 | `https://www.xiaohongshu.com/explore/52ba59b4cbb7bca4d156663d` | `52ba59b4cbb7bca4d156663d` | `52ba59b4cbb7bca4d156663d` | ✓ |
| 225 | `https://www.xiaohongshu.com/explore/523520a49547c9e6ff6b7c14` | `523520a49547c9e6ff6b7c14` | `523520a49547c9e6ff6b7c14` | ✓ |
| 226 | `https://www.xiaohongshu.com/explore/54c1bb0e55f2ccb4c31b3121` | `54c1bb0e55f2ccb4c31b3121` | `54c1bb0e55f2ccb4c31b3121` | ✓ |
| 227 | `https://www.xiaohongshu.com/explore/223ff4d10c000ee10d4c01f4` | `223ff4d10c000ee10d4c01f4` | `223ff4d10c000ee10d4c01f4` | ✓ |
| 228 | `https://www.xiaohongshu.com/explore/2d57300e3f0295d50ee5c870` | `2d57300e3f0295d50ee5c870` | `2d57300e3f0295d50ee5c870` | ✓ |
| 229 | `https://www.xiaohongshu.com/explore/01e54d3ea6d9db4da722a190` | `01e54d3ea6d9db4da722a190` | `01e54d3ea6d9db4da722a190` | ✓ |
| 230 | `https://www.xiaohongshu.com/explore/a7b7d6b677ba45596a62de9b` | `a7b7d6b677ba45596a62de9b` | `a7b7d6b677ba45596a62de9b` | ✓ |
| 231 | `https://www.xiaohongshu.com/explore/c7f3f320b1fc9239ad83821d` | `c7f3f320b1fc9239ad83821d` | `c7f3f320b1fc9239ad83821d` | ✓ |
| 232 | `https://www.xiaohongshu.com/explore/f8d609e562029202b20f5a45` | `f8d609e562029202b20f5a45` | `f8d609e562029202b20f5a45` | ✓ |
| 233 | `https://www.xiaohongshu.com/explore/985bf30aadd7f4e5782dccb4` | `985bf30aadd7f4e5782dccb4` | `985bf30aadd7f4e5782dccb4` | ✓ |
| 234 | `https://www.xiaohongshu.com/explore/6c3c28f78f88510f0fe68843` | `6c3c28f78f88510f0fe68843` | `6c3c28f78f88510f0fe68843` | ✓ |
| 235 | `https://www.xiaohongshu.com/explore/219d3512f11a1eebd3723a9b` | `219d3512f11a1eebd3723a9b` | `219d3512f11a1eebd3723a9b` | ✓ |
| 236 | `https://www.xiaohongshu.com/explore/c5310fde0969476ea91eeb16` | `c5310fde0969476ea91eeb16` | `c5310fde0969476ea91eeb16` | ✓ |
| 237 | `https://www.xiaohongshu.com/explore/17cdbfd8d9e13fdd1852792c` | `17cdbfd8d9e13fdd1852792c` | `17cdbfd8d9e13fdd1852792c` | ✓ |
| 238 | `https://www.xiaohongshu.com/explore/24bb812378be9e3a10e2764e` | `24bb812378be9e3a10e2764e` | `24bb812378be9e3a10e2764e` | ✓ |
| 239 | `https://www.xiaohongshu.com/explore/3139a73a3323d51c10b61470` | `3139a73a3323d51c10b61470` | `3139a73a3323d51c10b61470` | ✓ |
| 240 | `https://www.xiaohongshu.com/explore/5f01ae63a2d83c379bcdb0cd` | `5f01ae63a2d83c379bcdb0cd` | `5f01ae63a2d83c379bcdb0cd` | ✓ |
| 241 | `https://www.xiaohongshu.com/explore/b2c39dcca4bcce0b00c1f8d4` | `b2c39dcca4bcce0b00c1f8d4` | `b2c39dcca4bcce0b00c1f8d4` | ✓ |
| 242 | `https://www.xiaohongshu.com/explore/779b8099e88d70354e6c3872` | `779b8099e88d70354e6c3872` | `779b8099e88d70354e6c3872` | ✓ |
| 243 | `https://www.xiaohongshu.com/explore/ac8109f2d4ac20cd85a40f01` | `ac8109f2d4ac20cd85a40f01` | `ac8109f2d4ac20cd85a40f01` | ✓ |
| 244 | `https://www.xiaohongshu.com/explore/d3eb060ac70c5ecd95ed62d7` | `d3eb060ac70c5ecd95ed62d7` | `d3eb060ac70c5ecd95ed62d7` | ✓ |
| 245 | `https://www.xiaohongshu.com/explore/1aa47fa60b3b9187531a88f4` | `1aa47fa60b3b9187531a88f4` | `1aa47fa60b3b9187531a88f4` | ✓ |
| 246 | `https://www.xiaohongshu.com/explore/bf4f4513707de70cce7354d8` | `bf4f4513707de70cce7354d8` | `bf4f4513707de70cce7354d8` | ✓ |
| 247 | `https://www.xiaohongshu.com/explore/c8cdffb3a03725675baa1f48` | `c8cdffb3a03725675baa1f48` | `c8cdffb3a03725675baa1f48` | ✓ |
| 248 | `https://www.xiaohongshu.com/explore/4287a5a94eff9e7d403b4fbe` | `4287a5a94eff9e7d403b4fbe` | `4287a5a94eff9e7d403b4fbe` | ✓ |
| 249 | `https://www.xiaohongshu.com/explore/8dc629769776764a392d2177` | `8dc629769776764a392d2177` | `8dc629769776764a392d2177` | ✓ |
| 250 | `https://www.xiaohongshu.com/explore/dbaed8d75b3036173234cd2f` | `dbaed8d75b3036173234cd2f` | `dbaed8d75b3036173234cd2f` | ✓ |
| 251 | `https://www.xiaohongshu.com/explore/03bc9881c1fb53829be50586` | `03bc9881c1fb53829be50586` | `03bc9881c1fb53829be50586` | ✓ |
| 252 | `https://www.xiaohongshu.com/explore/d382f19ad5d454c9f9670be2` | `d382f19ad5d454c9f9670be2` | `d382f19ad5d454c9f9670be2` | ✓ |
| 253 | `https://www.xiaohongshu.com/explore/4673204219af489ecedec227` | `4673204219af489ecedec227` | `4673204219af489ecedec227` | ✓ |
| 254 | `https://www.xiaohongshu.com/explore/14103170c09c7b29a53c2c9c` | `14103170c09c7b29a53c2c9c` | `14103170c09c7b29a53c2c9c` | ✓ |
| 255 | `https://www.xiaohongshu.com/explore/9b9542cac88617ac39607f18` | `9b9542cac88617ac39607f18` | `9b9542cac88617ac39607f18` | ✓ |
| 256 | `https://www.xiaohongshu.com/explore/a7fa8763d9b01394ead73ac2` | `a7fa8763d9b01394ead73ac2` | `a7fa8763d9b01394ead73ac2` | ✓ |
| 257 | `https://www.xiaohongshu.com/explore/781b267833d4f1b52ea528f7` | `781b267833d4f1b52ea528f7` | `781b267833d4f1b52ea528f7` | ✓ |
| 258 | `https://www.xiaohongshu.com/explore/9ef923169827d095f8a73362` | `9ef923169827d095f8a73362` | `9ef923169827d095f8a73362` | ✓ |
| 259 | `https://www.xiaohongshu.com/explore/9d6fcfae434e8ca38a8791e4` | `9d6fcfae434e8ca38a8791e4` | `9d6fcfae434e8ca38a8791e4` | ✓ |
| 260 | `https://www.xiaohongshu.com/explore/562564a40f35b6109b91d365` | `562564a40f35b6109b91d365` | `562564a40f35b6109b91d365` | ✓ |
| 261 | `https://www.xiaohongshu.com/explore/c74f640afb9b5cc251570507` | `c74f640afb9b5cc251570507` | `c74f640afb9b5cc251570507` | ✓ |
| 262 | `https://www.xiaohongshu.com/explore/e38691c7210eaaeb0bc4ceaf` | `e38691c7210eaaeb0bc4ceaf` | `e38691c7210eaaeb0bc4ceaf` | ✓ |
| 263 | `https://www.xiaohongshu.com/explore/f9662cb650ec2e1fea1c529e` | `f9662cb650ec2e1fea1c529e` | `f9662cb650ec2e1fea1c529e` | ✓ |
| 264 | `https://www.xiaohongshu.com/explore/f7752af0200da5854ccfc36a` | `f7752af0200da5854ccfc36a` | `f7752af0200da5854ccfc36a` | ✓ |
| 265 | `https://www.xiaohongshu.com/explore/d6f0ad47f05d035ed5e89965` | `d6f0ad47f05d035ed5e89965` | `d6f0ad47f05d035ed5e89965` | ✓ |
| 266 | `https://www.xiaohongshu.com/explore/39f677f30db13bff49dd1c47` | `39f677f30db13bff49dd1c47` | `39f677f30db13bff49dd1c47` | ✓ |
| 267 | `https://www.xiaohongshu.com/explore/72fa5bf66cd40f59624cab48` | `72fa5bf66cd40f59624cab48` | `72fa5bf66cd40f59624cab48` | ✓ |
| 268 | `https://www.xiaohongshu.com/explore/209ea8f4e04aa4abc12fc284` | `209ea8f4e04aa4abc12fc284` | `209ea8f4e04aa4abc12fc284` | ✓ |
| 269 | `https://www.xiaohongshu.com/explore/1f36ebf1b66f3097b1d36d36` | `1f36ebf1b66f3097b1d36d36` | `1f36ebf1b66f3097b1d36d36` | ✓ |
| 270 | `https://www.xiaohongshu.com/explore/7393a3b350f6f1f3892da227` | `7393a3b350f6f1f3892da227` | `7393a3b350f6f1f3892da227` | ✓ |
| 271 | `https://www.xiaohongshu.com/explore/fe4ca58f6dcd3ac21e750ae4` | `fe4ca58f6dcd3ac21e750ae4` | `fe4ca58f6dcd3ac21e750ae4` | ✓ |
| 272 | `https://www.xiaohongshu.com/explore/8ba280172c2e196a49c496f2` | `8ba280172c2e196a49c496f2` | `8ba280172c2e196a49c496f2` | ✓ |
| 273 | `https://www.xiaohongshu.com/explore/cf659d940daab5187baf2145` | `cf659d940daab5187baf2145` | `cf659d940daab5187baf2145` | ✓ |
| 274 | `https://www.xiaohongshu.com/explore/8f565bd2b22f7644d209fda6` | `8f565bd2b22f7644d209fda6` | `8f565bd2b22f7644d209fda6` | ✓ |
| 275 | `https://www.xiaohongshu.com/explore/22840976e7f5dc2b6a1bd93c` | `22840976e7f5dc2b6a1bd93c` | `22840976e7f5dc2b6a1bd93c` | ✓ |
| 276 | `https://www.xiaohongshu.com/explore/eb3dc3a968bd88e4b7bcf3fa` | `eb3dc3a968bd88e4b7bcf3fa` | `eb3dc3a968bd88e4b7bcf3fa` | ✓ |
| 277 | `https://www.xiaohongshu.com/explore/3c0e23b2b6e071c57c870344` | `3c0e23b2b6e071c57c870344` | `3c0e23b2b6e071c57c870344` | ✓ |
| 278 | `https://www.xiaohongshu.com/explore/6b6fdf561ce7c09956ce39d3` | `6b6fdf561ce7c09956ce39d3` | `6b6fdf561ce7c09956ce39d3` | ✓ |
| 279 | `https://www.xiaohongshu.com/explore/00ff7e3d7456aecb074b5443` | `00ff7e3d7456aecb074b5443` | `00ff7e3d7456aecb074b5443` | ✓ |
| 280 | `https://www.xiaohongshu.com/explore/3d7018e0b23248eb4d2f111f` | `3d7018e0b23248eb4d2f111f` | `3d7018e0b23248eb4d2f111f` | ✓ |
| 281 | `https://www.xiaohongshu.com/explore/a36a60195180c5cad00768d9` | `a36a60195180c5cad00768d9` | `a36a60195180c5cad00768d9` | ✓ |
| 282 | `https://www.xiaohongshu.com/explore/533f5bb412bf6dddebd310bd` | `533f5bb412bf6dddebd310bd` | `533f5bb412bf6dddebd310bd` | ✓ |
| 283 | `https://www.xiaohongshu.com/explore/c226109983153186fbf65ffd` | `c226109983153186fbf65ffd` | `c226109983153186fbf65ffd` | ✓ |
| 284 | `https://www.xiaohongshu.com/explore/c0ca1625ee3f2ee240aeca6b` | `c0ca1625ee3f2ee240aeca6b` | `c0ca1625ee3f2ee240aeca6b` | ✓ |
| 285 | `https://www.xiaohongshu.com/explore/8ebf2ad84e699676bb193c83` | `8ebf2ad84e699676bb193c83` | `8ebf2ad84e699676bb193c83` | ✓ |
| 286 | `https://www.xiaohongshu.com/explore/f32b8d01801e48a7217d2b3b` | `f32b8d01801e48a7217d2b3b` | `f32b8d01801e48a7217d2b3b` | ✓ |
| 287 | `https://www.xiaohongshu.com/explore/be2b4cb7ee0760ddffaf9d2d` | `be2b4cb7ee0760ddffaf9d2d` | `be2b4cb7ee0760ddffaf9d2d` | ✓ |
| 288 | `https://www.xiaohongshu.com/explore/7947da157c73c33380fcd479` | `7947da157c73c33380fcd479` | `7947da157c73c33380fcd479` | ✓ |
| 289 | `https://www.xiaohongshu.com/explore/9b0396c75ad4f538f538c5dc` | `9b0396c75ad4f538f538c5dc` | `9b0396c75ad4f538f538c5dc` | ✓ |
| 290 | `https://www.xiaohongshu.com/explore/2509d73300bec6c47bb23cc3` | `2509d73300bec6c47bb23cc3` | `2509d73300bec6c47bb23cc3` | ✓ |
| 291 | `https://www.xiaohongshu.com/explore/6711f84dd14ad4bfd602141e` | `6711f84dd14ad4bfd602141e` | `6711f84dd14ad4bfd602141e` | ✓ |
| 292 | `https://www.xiaohongshu.com/explore/df23f19b2c1e57d13a403092` | `df23f19b2c1e57d13a403092` | `df23f19b2c1e57d13a403092` | ✓ |
| 293 | `https://www.xiaohongshu.com/explore/78f8b8ea603023d4bc32c511` | `78f8b8ea603023d4bc32c511` | `78f8b8ea603023d4bc32c511` | ✓ |
| 294 | `https://www.xiaohongshu.com/explore/4608dd15c8aafa6d85167c88` | `4608dd15c8aafa6d85167c88` | `4608dd15c8aafa6d85167c88` | ✓ |
| 295 | `https://www.xiaohongshu.com/explore/cddc62c895859aca69642d65` | `cddc62c895859aca69642d65` | `cddc62c895859aca69642d65` | ✓ |
| 296 | `https://www.xiaohongshu.com/explore/eb44b9baa5ba99c69d00bea5` | `eb44b9baa5ba99c69d00bea5` | `eb44b9baa5ba99c69d00bea5` | ✓ |
| 297 | `https://www.xiaohongshu.com/explore/1e1551d5d7cb86201a8e637c` | `1e1551d5d7cb86201a8e637c` | `1e1551d5d7cb86201a8e637c` | ✓ |
| 298 | `https://www.xiaohongshu.com/explore/5cc4d4abef72b9a11f3372d7` | `5cc4d4abef72b9a11f3372d7` | `5cc4d4abef72b9a11f3372d7` | ✓ |
| 299 | `https://www.xiaohongshu.com/explore/ac7a2c288f23ee3da2d975ef` | `ac7a2c288f23ee3da2d975ef` | `ac7a2c288f23ee3da2d975ef` | ✓ |
| 300 | `https://www.xiaohongshu.com/explore/03624eb7aa937f4242ebe23e` | `03624eb7aa937f4242ebe23e` | `03624eb7aa937f4242ebe23e` | ✓ |
| 301 | `https://www.xiaohongshu.com/explore/5da635931490ceb1e328a6ee` | `5da635931490ceb1e328a6ee` | `5da635931490ceb1e328a6ee` | ✓ |
| 302 | `https://www.xiaohongshu.com/explore/4104614a17644b3fed9a5ebe` | `4104614a17644b3fed9a5ebe` | `4104614a17644b3fed9a5ebe` | ✓ |
| 303 | `https://www.xiaohongshu.com/explore/a38f2212b59207832a81003c` | `a38f2212b59207832a81003c` | `a38f2212b59207832a81003c` | ✓ |
| 304 | `https://www.xiaohongshu.com/explore/8ad3f3946af0e7651c8ca6c9` | `8ad3f3946af0e7651c8ca6c9` | `8ad3f3946af0e7651c8ca6c9` | ✓ |
| 305 | `https://www.xiaohongshu.com/explore/701f03be53767bad251ce947` | `701f03be53767bad251ce947` | `701f03be53767bad251ce947` | ✓ |
| 306 | `https://www.xiaohongshu.com/explore/26c7bd6cd7dd17b504c18408` | `26c7bd6cd7dd17b504c18408` | `26c7bd6cd7dd17b504c18408` | ✓ |
| 307 | `https://www.xiaohongshu.com/explore/5142c77c78a49ee3032bc273` | `5142c77c78a49ee3032bc273` | `5142c77c78a49ee3032bc273` | ✓ |
| 308 | `https://www.xiaohongshu.com/explore/1a940200be2b62271b6e8ee7` | `1a940200be2b62271b6e8ee7` | `1a940200be2b62271b6e8ee7` | ✓ |
| 309 | `https://www.xiaohongshu.com/explore/2a19cac73cc35e7f5deb5390` | `2a19cac73cc35e7f5deb5390` | `2a19cac73cc35e7f5deb5390` | ✓ |
| 310 | `https://www.xiaohongshu.com/explore/ee7c94f19dbcac0eb72f021a` | `ee7c94f19dbcac0eb72f021a` | `ee7c94f19dbcac0eb72f021a` | ✓ |
| 311 | `https://www.xiaohongshu.com/explore/7261f583ce9643b4cb949a17` | `7261f583ce9643b4cb949a17` | `7261f583ce9643b4cb949a17` | ✓ |
| 312 | `https://www.xiaohongshu.com/explore/50fa55765a476bb73007e370` | `50fa55765a476bb73007e370` | `50fa55765a476bb73007e370` | ✓ |
| 313 | `https://www.xiaohongshu.com/explore/70b7f9588f6c6159dc04e64c` | `70b7f9588f6c6159dc04e64c` | `70b7f9588f6c6159dc04e64c` | ✓ |
| 314 | `https://www.xiaohongshu.com/explore/c9f16bd2f0191e5ebd9858d7` | `c9f16bd2f0191e5ebd9858d7` | `c9f16bd2f0191e5ebd9858d7` | ✓ |
| 315 | `https://www.xiaohongshu.com/explore/9438fccb1d0e09a263232cc4` | `9438fccb1d0e09a263232cc4` | `9438fccb1d0e09a263232cc4` | ✓ |
| 316 | `https://www.xiaohongshu.com/explore/350b43739f826f9d176af1d2` | `350b43739f826f9d176af1d2` | `350b43739f826f9d176af1d2` | ✓ |
| 317 | `https://www.xiaohongshu.com/explore/f9735720496ac8a0c4692c49` | `f9735720496ac8a0c4692c49` | `f9735720496ac8a0c4692c49` | ✓ |
| 318 | `https://www.xiaohongshu.com/explore/a362a4586cf5419dcb892e8b` | `a362a4586cf5419dcb892e8b` | `a362a4586cf5419dcb892e8b` | ✓ |
| 319 | `https://www.xiaohongshu.com/explore/f5f9b917d92a7e8b2f85d8b5` | `f5f9b917d92a7e8b2f85d8b5` | `f5f9b917d92a7e8b2f85d8b5` | ✓ |
| 320 | `https://www.xiaohongshu.com/explore/ffd57ae8541b4dd2e01007e6` | `ffd57ae8541b4dd2e01007e6` | `ffd57ae8541b4dd2e01007e6` | ✓ |
| 321 | `https://www.xiaohongshu.com/explore/d9305ebfcb221d23117131d7` | `d9305ebfcb221d23117131d7` | `d9305ebfcb221d23117131d7` | ✓ |
| 322 | `https://www.xiaohongshu.com/explore/c270c8e64f211050ade5d009` | `c270c8e64f211050ade5d009` | `c270c8e64f211050ade5d009` | ✓ |
| 323 | `https://www.xiaohongshu.com/explore/2af390fe3ff9166c7e6d16ff` | `2af390fe3ff9166c7e6d16ff` | `2af390fe3ff9166c7e6d16ff` | ✓ |
| 324 | `https://www.xiaohongshu.com/explore/af9372c480e5e3a993849955` | `af9372c480e5e3a993849955` | `af9372c480e5e3a993849955` | ✓ |
| 325 | `https://www.xiaohongshu.com/explore/bf7c6b510f000ffb4f9b4124` | `bf7c6b510f000ffb4f9b4124` | `bf7c6b510f000ffb4f9b4124` | ✓ |
| 326 | `https://www.xiaohongshu.com/explore/8a103308c64709881dc03624` | `8a103308c64709881dc03624` | `8a103308c64709881dc03624` | ✓ |
| 327 | `https://www.xiaohongshu.com/explore/9017b14506c2d45c3483339b` | `9017b14506c2d45c3483339b` | `9017b14506c2d45c3483339b` | ✓ |
| 328 | `https://www.xiaohongshu.com/explore/7a6f290ea61575f78a68b975` | `7a6f290ea61575f78a68b975` | `7a6f290ea61575f78a68b975` | ✓ |
| 329 | `https://www.xiaohongshu.com/explore/83fbdd136cd87902dbe63fb1` | `83fbdd136cd87902dbe63fb1` | `83fbdd136cd87902dbe63fb1` | ✓ |
| 330 | `https://www.xiaohongshu.com/explore/c44155ae78351e825475a38e` | `c44155ae78351e825475a38e` | `c44155ae78351e825475a38e` | ✓ |
| 331 | `https://www.xiaohongshu.com/explore/fbba7d2216cecd79b0a15282` | `fbba7d2216cecd79b0a15282` | `fbba7d2216cecd79b0a15282` | ✓ |
| 332 | `https://www.xiaohongshu.com/explore/362c5da220b1e98dd27bcbb1` | `362c5da220b1e98dd27bcbb1` | `362c5da220b1e98dd27bcbb1` | ✓ |
| 333 | `https://www.xiaohongshu.com/explore/9a22d58607d5830c0b9bb01a` | `9a22d58607d5830c0b9bb01a` | `9a22d58607d5830c0b9bb01a` | ✓ |
| 334 | `https://www.xiaohongshu.com/explore/2794e0c39b97484ff74cebbf` | `2794e0c39b97484ff74cebbf` | `2794e0c39b97484ff74cebbf` | ✓ |
| 335 | `https://www.xiaohongshu.com/explore/1188f43488135ee194bab38f` | `1188f43488135ee194bab38f` | `1188f43488135ee194bab38f` | ✓ |
| 336 | `https://www.xiaohongshu.com/explore/4c51b5f43fb23ec7831a9534` | `4c51b5f43fb23ec7831a9534` | `4c51b5f43fb23ec7831a9534` | ✓ |
| 337 | `https://www.xiaohongshu.com/explore/2ebffa403f0da05c1724d2a7` | `2ebffa403f0da05c1724d2a7` | `2ebffa403f0da05c1724d2a7` | ✓ |
| 338 | `https://www.xiaohongshu.com/explore/7b7404cb4879483baeff1dc7` | `7b7404cb4879483baeff1dc7` | `7b7404cb4879483baeff1dc7` | ✓ |
| 339 | `https://www.xiaohongshu.com/explore/91e09e0e2d5b057177d8374b` | `91e09e0e2d5b057177d8374b` | `91e09e0e2d5b057177d8374b` | ✓ |
| 340 | `https://www.xiaohongshu.com/explore/e7f8974c8796e533f49286be` | `e7f8974c8796e533f49286be` | `e7f8974c8796e533f49286be` | ✓ |
| 341 | `https://www.xiaohongshu.com/explore/5f2312f40b85789062e13714` | `5f2312f40b85789062e13714` | `5f2312f40b85789062e13714` | ✓ |
| 342 | `https://www.xiaohongshu.com/explore/4e4246eaf038ede29a2eec87` | `4e4246eaf038ede29a2eec87` | `4e4246eaf038ede29a2eec87` | ✓ |
| 343 | `https://www.xiaohongshu.com/explore/88ef5b7d1f5429e2c3cbaaca` | `88ef5b7d1f5429e2c3cbaaca` | `88ef5b7d1f5429e2c3cbaaca` | ✓ |
| 344 | `https://www.xiaohongshu.com/explore/85861b6b1264cafa9d31abf4` | `85861b6b1264cafa9d31abf4` | `85861b6b1264cafa9d31abf4` | ✓ |
| 345 | `https://www.xiaohongshu.com/explore/1aae3b02de8d393cccefb5b0` | `1aae3b02de8d393cccefb5b0` | `1aae3b02de8d393cccefb5b0` | ✓ |
| 346 | `https://www.xiaohongshu.com/explore/1fe399ac22393f78cb826634` | `1fe399ac22393f78cb826634` | `1fe399ac22393f78cb826634` | ✓ |
| 347 | `https://www.xiaohongshu.com/explore/015312991bcd43c1d6ab4045` | `015312991bcd43c1d6ab4045` | `015312991bcd43c1d6ab4045` | ✓ |
| 348 | `https://www.xiaohongshu.com/explore/43441f758e117e48138c7b06` | `43441f758e117e48138c7b06` | `43441f758e117e48138c7b06` | ✓ |
| 349 | `https://www.xiaohongshu.com/explore/f6ac359a82bf4e9287027ee0` | `f6ac359a82bf4e9287027ee0` | `f6ac359a82bf4e9287027ee0` | ✓ |
| 350 | `https://www.xiaohongshu.com/explore/75a7513089c7e4d72e50913f` | `75a7513089c7e4d72e50913f` | `75a7513089c7e4d72e50913f` | ✓ |
| 351 | `https://www.xiaohongshu.com/explore/6be7e00a57c79051909e4be5` | `6be7e00a57c79051909e4be5` | `6be7e00a57c79051909e4be5` | ✓ |
| 352 | `https://www.xiaohongshu.com/explore/fc9bb2d5eb0a5c15cb6d6d0e` | `fc9bb2d5eb0a5c15cb6d6d0e` | `fc9bb2d5eb0a5c15cb6d6d0e` | ✓ |
| 353 | `https://www.xiaohongshu.com/explore/b200d2bc97b5e92abe5eb387` | `b200d2bc97b5e92abe5eb387` | `b200d2bc97b5e92abe5eb387` | ✓ |
| 354 | `https://www.xiaohongshu.com/explore/e00e5acbc8db133d90807ff0` | `e00e5acbc8db133d90807ff0` | `e00e5acbc8db133d90807ff0` | ✓ |
| 355 | `https://www.xiaohongshu.com/explore/8a7b86c9c4fd01f79ce2ed52` | `8a7b86c9c4fd01f79ce2ed52` | `8a7b86c9c4fd01f79ce2ed52` | ✓ |
| 356 | `https://www.xiaohongshu.com/explore/18b92e805d524311e7b85bed` | `18b92e805d524311e7b85bed` | `18b92e805d524311e7b85bed` | ✓ |
| 357 | `https://www.xiaohongshu.com/explore/d6c8a112c7ea53deb12a8959` | `d6c8a112c7ea53deb12a8959` | `d6c8a112c7ea53deb12a8959` | ✓ |
| 358 | `https://www.xiaohongshu.com/explore/fbeb52239dd8ae1b7d6ecece` | `fbeb52239dd8ae1b7d6ecece` | `fbeb52239dd8ae1b7d6ecece` | ✓ |
| 359 | `https://www.xiaohongshu.com/explore/47ad869a4c5e16afe2fe1ad4` | `47ad869a4c5e16afe2fe1ad4` | `47ad869a4c5e16afe2fe1ad4` | ✓ |
| 360 | `https://www.xiaohongshu.com/explore/ab37b24e6950310bc7528c5a` | `ab37b24e6950310bc7528c5a` | `ab37b24e6950310bc7528c5a` | ✓ |
| 361 | `https://www.xiaohongshu.com/explore/e19f0c53face754300010172` | `e19f0c53face754300010172` | `e19f0c53face754300010172` | ✓ |
| 362 | `https://www.xiaohongshu.com/explore/8f94ab64bafc4a4bf2b9dbe9` | `8f94ab64bafc4a4bf2b9dbe9` | `8f94ab64bafc4a4bf2b9dbe9` | ✓ |
| 363 | `https://www.xiaohongshu.com/explore/eac7aa82161c3a07128feba9` | `eac7aa82161c3a07128feba9` | `eac7aa82161c3a07128feba9` | ✓ |
| 364 | `https://www.xiaohongshu.com/explore/78ecd183b80ed38bcbf99856` | `78ecd183b80ed38bcbf99856` | `78ecd183b80ed38bcbf99856` | ✓ |
| 365 | `https://www.xiaohongshu.com/explore/fa65b1046af3b100feebc218` | `fa65b1046af3b100feebc218` | `fa65b1046af3b100feebc218` | ✓ |
| 366 | `https://www.xiaohongshu.com/explore/2c6e58775a2c01b522e95f77` | `2c6e58775a2c01b522e95f77` | `2c6e58775a2c01b522e95f77` | ✓ |
| 367 | `https://www.xiaohongshu.com/explore/4a2b60e5d769afa8162805bd` | `4a2b60e5d769afa8162805bd` | `4a2b60e5d769afa8162805bd` | ✓ |
| 368 | `https://www.xiaohongshu.com/explore/7c7d9b96d15033e012a956f9` | `7c7d9b96d15033e012a956f9` | `7c7d9b96d15033e012a956f9` | ✓ |
| 369 | `https://www.xiaohongshu.com/explore/efe8db809dee889631857cc6` | `efe8db809dee889631857cc6` | `efe8db809dee889631857cc6` | ✓ |
| 370 | `https://www.xiaohongshu.com/explore/899488a55c65e160286804ef` | `899488a55c65e160286804ef` | `899488a55c65e160286804ef` | ✓ |
| 371 | `https://www.xiaohongshu.com/explore/7969460035a39e1112bed8c4` | `7969460035a39e1112bed8c4` | `7969460035a39e1112bed8c4` | ✓ |
| 372 | `https://www.xiaohongshu.com/explore/be20e2df8bf57eaeb8a17961` | `be20e2df8bf57eaeb8a17961` | `be20e2df8bf57eaeb8a17961` | ✓ |
| 373 | `https://www.xiaohongshu.com/explore/602e68c2d05717cdd459b9f2` | `602e68c2d05717cdd459b9f2` | `602e68c2d05717cdd459b9f2` | ✓ |
| 374 | `https://www.xiaohongshu.com/explore/cd63bd3c416aa64120efd110` | `cd63bd3c416aa64120efd110` | `cd63bd3c416aa64120efd110` | ✓ |
| 375 | `https://www.xiaohongshu.com/explore/e57cbf06e096fd3627d851cf` | `e57cbf06e096fd3627d851cf` | `e57cbf06e096fd3627d851cf` | ✓ |
| 376 | `https://www.xiaohongshu.com/explore/0258ee9daacd86f1ed77cc9f` | `0258ee9daacd86f1ed77cc9f` | `0258ee9daacd86f1ed77cc9f` | ✓ |
| 377 | `https://www.xiaohongshu.com/explore/7b5d160737c4c539f277e70e` | `7b5d160737c4c539f277e70e` | `7b5d160737c4c539f277e70e` | ✓ |
| 378 | `https://www.xiaohongshu.com/explore/f5a37e61050ff3bcbe9ca7be` | `f5a37e61050ff3bcbe9ca7be` | `f5a37e61050ff3bcbe9ca7be` | ✓ |
| 379 | `https://www.xiaohongshu.com/explore/31e842fdbc03148db17ac660` | `31e842fdbc03148db17ac660` | `31e842fdbc03148db17ac660` | ✓ |
| 380 | `https://www.xiaohongshu.com/explore/c170e64c2107bffaa81a2909` | `c170e64c2107bffaa81a2909` | `c170e64c2107bffaa81a2909` | ✓ |
| 381 | `https://www.xiaohongshu.com/explore/d151fa0fe2cc7583424950e3` | `d151fa0fe2cc7583424950e3` | `d151fa0fe2cc7583424950e3` | ✓ |
| 382 | `https://www.xiaohongshu.com/explore/a99f5518d9029065be3a2e7e` | `a99f5518d9029065be3a2e7e` | `a99f5518d9029065be3a2e7e` | ✓ |
| 383 | `https://www.xiaohongshu.com/explore/9b81ce4ffbd441f9d161e20e` | `9b81ce4ffbd441f9d161e20e` | `9b81ce4ffbd441f9d161e20e` | ✓ |
| 384 | `https://www.xiaohongshu.com/explore/340b06ba6b69197ab8116c35` | `340b06ba6b69197ab8116c35` | `340b06ba6b69197ab8116c35` | ✓ |
| 385 | `https://www.xiaohongshu.com/explore/fd535cdf598b41599f8e131d` | `fd535cdf598b41599f8e131d` | `fd535cdf598b41599f8e131d` | ✓ |
| 386 | `https://www.xiaohongshu.com/explore/ebf6df8b44d020e5e96354fd` | `ebf6df8b44d020e5e96354fd` | `ebf6df8b44d020e5e96354fd` | ✓ |
| 387 | `https://www.xiaohongshu.com/explore/feb83d49b521b359e8e71750` | `feb83d49b521b359e8e71750` | `feb83d49b521b359e8e71750` | ✓ |
| 388 | `https://www.xiaohongshu.com/explore/1945b8bf36ff1423f78340bc` | `1945b8bf36ff1423f78340bc` | `1945b8bf36ff1423f78340bc` | ✓ |
| 389 | `https://www.xiaohongshu.com/explore/94ac44f6a52130e7d1943281` | `94ac44f6a52130e7d1943281` | `94ac44f6a52130e7d1943281` | ✓ |
| 390 | `https://www.xiaohongshu.com/explore/551a5c7e77addcac708026d5` | `551a5c7e77addcac708026d5` | `551a5c7e77addcac708026d5` | ✓ |
| 391 | `https://www.xiaohongshu.com/explore/2d7060a30c689ace2fdc10c4` | `2d7060a30c689ace2fdc10c4` | `2d7060a30c689ace2fdc10c4` | ✓ |
| 392 | `https://www.xiaohongshu.com/explore/26a504c2057dae708c7bbaa9` | `26a504c2057dae708c7bbaa9` | `26a504c2057dae708c7bbaa9` | ✓ |
| 393 | `https://www.xiaohongshu.com/explore/b972c8a6c3b7091a08868d4e` | `b972c8a6c3b7091a08868d4e` | `b972c8a6c3b7091a08868d4e` | ✓ |
| 394 | `https://www.xiaohongshu.com/explore/457d7bc120aa06aa7fdc04c5` | `457d7bc120aa06aa7fdc04c5` | `457d7bc120aa06aa7fdc04c5` | ✓ |
| 395 | `https://www.xiaohongshu.com/explore/1c735994b892992466b29627` | `1c735994b892992466b29627` | `1c735994b892992466b29627` | ✓ |
| 396 | `https://www.xiaohongshu.com/explore/6b2a34c9c3bd8b8e49fb6bcb` | `6b2a34c9c3bd8b8e49fb6bcb` | `6b2a34c9c3bd8b8e49fb6bcb` | ✓ |
| 397 | `https://www.xiaohongshu.com/explore/f84fc69a871b466e4edc3e75` | `f84fc69a871b466e4edc3e75` | `f84fc69a871b466e4edc3e75` | ✓ |
| 398 | `https://www.xiaohongshu.com/explore/8386571d2708469d72de0aec` | `8386571d2708469d72de0aec` | `8386571d2708469d72de0aec` | ✓ |
| 399 | `https://www.xiaohongshu.com/explore/7fa55fee43f6ad39fe3f85c9` | `7fa55fee43f6ad39fe3f85c9` | `7fa55fee43f6ad39fe3f85c9` | ✓ |
| 400 | `https://www.xiaohongshu.com/explore/884addd750edd8b935d40bc9` | `884addd750edd8b935d40bc9` | `884addd750edd8b935d40bc9` | ✓ |

### explore_with_params 类型

> 带查询参数的 explore 链接，如 xsec_token、source 等
>
> 共 150 个测试案例

| # | URL | 期望ID | 实际ID | 结果 |
|---|-----|--------|--------|------|
| 1 | `https://www.xiaohongshu.com/explore/a85eeac9801da3849a08c1d1...` | `a85eeac9801da3849a08c1d1` | `a85eeac9801da3849a08c1d1` | ✓ |
| 2 | `https://www.xiaohongshu.com/explore/4e1b23b71e3ab321ec6ed293...` | `4e1b23b71e3ab321ec6ed293` | `4e1b23b71e3ab321ec6ed293` | ✓ |
| 3 | `https://www.xiaohongshu.com/explore/d41779d8790bf15ee53358fd...` | `d41779d8790bf15ee53358fd` | `d41779d8790bf15ee53358fd` | ✓ |
| 4 | `https://www.xiaohongshu.com/explore/0f4824864eb75c409aab2ad5...` | `0f4824864eb75c409aab2ad5` | `0f4824864eb75c409aab2ad5` | ✓ |
| 5 | `https://www.xiaohongshu.com/explore/f82e2e4dde581ed56a9d4755` | `f82e2e4dde581ed56a9d4755` | `f82e2e4dde581ed56a9d4755` | ✓ |
| 6 | `https://www.xiaohongshu.com/explore/0369ad5bfa18db6319628307...` | `0369ad5bfa18db6319628307` | `0369ad5bfa18db6319628307` | ✓ |
| 7 | `https://www.xiaohongshu.com/explore/6889ee0b04f25a2ac11124f7` | `6889ee0b04f25a2ac11124f7` | `6889ee0b04f25a2ac11124f7` | ✓ |
| 8 | `https://www.xiaohongshu.com/explore/7a1c4723c1bf3daec0a93af5...` | `7a1c4723c1bf3daec0a93af5` | `7a1c4723c1bf3daec0a93af5` | ✓ |
| 9 | `https://www.xiaohongshu.com/explore/3435ec8c42afa883e8954daa...` | `3435ec8c42afa883e8954daa` | `3435ec8c42afa883e8954daa` | ✓ |
| 10 | `https://www.xiaohongshu.com/explore/a9e4b8f9125c47540f53c1d4...` | `a9e4b8f9125c47540f53c1d4` | `a9e4b8f9125c47540f53c1d4` | ✓ |
| 11 | `https://www.xiaohongshu.com/explore/3012e7ba73ad01523bef0251...` | `3012e7ba73ad01523bef0251` | `3012e7ba73ad01523bef0251` | ✓ |
| 12 | `https://www.xiaohongshu.com/explore/1d47e8600f031fc6127cb9dc...` | `1d47e8600f031fc6127cb9dc` | `1d47e8600f031fc6127cb9dc` | ✓ |
| 13 | `https://www.xiaohongshu.com/explore/b6950e76a00623e6aa323fcf` | `b6950e76a00623e6aa323fcf` | `b6950e76a00623e6aa323fcf` | ✓ |
| 14 | `https://www.xiaohongshu.com/explore/43444892996c04ac6960a922...` | `43444892996c04ac6960a922` | `43444892996c04ac6960a922` | ✓ |
| 15 | `https://www.xiaohongshu.com/explore/32bf174fcbb6e706449fc6b4...` | `32bf174fcbb6e706449fc6b4` | `32bf174fcbb6e706449fc6b4` | ✓ |
| 16 | `https://www.xiaohongshu.com/explore/0510d0d24e3964a015f30ba8...` | `0510d0d24e3964a015f30ba8` | `0510d0d24e3964a015f30ba8` | ✓ |
| 17 | `https://www.xiaohongshu.com/explore/12fab16869b9cc7345ed69d1...` | `12fab16869b9cc7345ed69d1` | `12fab16869b9cc7345ed69d1` | ✓ |
| 18 | `https://www.xiaohongshu.com/explore/ceaacbdff4c8021d147de417...` | `ceaacbdff4c8021d147de417` | `ceaacbdff4c8021d147de417` | ✓ |
| 19 | `https://www.xiaohongshu.com/explore/e2d8cc19461fa319f61a4e06` | `e2d8cc19461fa319f61a4e06` | `e2d8cc19461fa319f61a4e06` | ✓ |
| 20 | `https://www.xiaohongshu.com/explore/83bb5fc2752adfe17c6ca2da...` | `83bb5fc2752adfe17c6ca2da` | `83bb5fc2752adfe17c6ca2da` | ✓ |
| 21 | `https://www.xiaohongshu.com/explore/7b5ccac658fd05a12761e840...` | `7b5ccac658fd05a12761e840` | `7b5ccac658fd05a12761e840` | ✓ |
| 22 | `https://www.xiaohongshu.com/explore/3bf4f97035fe3cbe864d4209...` | `3bf4f97035fe3cbe864d4209` | `3bf4f97035fe3cbe864d4209` | ✓ |
| 23 | `https://www.xiaohongshu.com/explore/56a7e47f9adda36a89779965` | `56a7e47f9adda36a89779965` | `56a7e47f9adda36a89779965` | ✓ |
| 24 | `https://www.xiaohongshu.com/explore/c0d0fe614bee743ca448d65f...` | `c0d0fe614bee743ca448d65f` | `c0d0fe614bee743ca448d65f` | ✓ |
| 25 | `https://www.xiaohongshu.com/explore/e803fed26b85bc76211d87d9` | `e803fed26b85bc76211d87d9` | `e803fed26b85bc76211d87d9` | ✓ |
| 26 | `https://www.xiaohongshu.com/explore/de6fc317d4efa245fab1edb4...` | `de6fc317d4efa245fab1edb4` | `de6fc317d4efa245fab1edb4` | ✓ |
| 27 | `https://www.xiaohongshu.com/explore/c3701176bcc04efa9f165907...` | `c3701176bcc04efa9f165907` | `c3701176bcc04efa9f165907` | ✓ |
| 28 | `https://www.xiaohongshu.com/explore/8da205cea81340b8d787d9fb...` | `8da205cea81340b8d787d9fb` | `8da205cea81340b8d787d9fb` | ✓ |
| 29 | `https://www.xiaohongshu.com/explore/3cebf626db57e95f87b90d8c...` | `3cebf626db57e95f87b90d8c` | `3cebf626db57e95f87b90d8c` | ✓ |
| 30 | `https://www.xiaohongshu.com/explore/4a67be300689e69a7c2c940d` | `4a67be300689e69a7c2c940d` | `4a67be300689e69a7c2c940d` | ✓ |
| 31 | `https://www.xiaohongshu.com/explore/d06c54759b88a1ca3f594567...` | `d06c54759b88a1ca3f594567` | `d06c54759b88a1ca3f594567` | ✓ |
| 32 | `https://www.xiaohongshu.com/explore/6e34dd85d13738c234622910...` | `6e34dd85d13738c234622910` | `6e34dd85d13738c234622910` | ✓ |
| 33 | `https://www.xiaohongshu.com/explore/820edc20a481f9b11604e1b4` | `820edc20a481f9b11604e1b4` | `820edc20a481f9b11604e1b4` | ✓ |
| 34 | `https://www.xiaohongshu.com/explore/32aaf8a27fbe3c8694d1bdac...` | `32aaf8a27fbe3c8694d1bdac` | `32aaf8a27fbe3c8694d1bdac` | ✓ |
| 35 | `https://www.xiaohongshu.com/explore/57bf2f18ece73772f13cd331` | `57bf2f18ece73772f13cd331` | `57bf2f18ece73772f13cd331` | ✓ |
| 36 | `https://www.xiaohongshu.com/explore/02adce339d499b0f8296296f...` | `02adce339d499b0f8296296f` | `02adce339d499b0f8296296f` | ✓ |
| 37 | `https://www.xiaohongshu.com/explore/75d7a136d9b17a88383d5f44...` | `75d7a136d9b17a88383d5f44` | `75d7a136d9b17a88383d5f44` | ✓ |
| 38 | `https://www.xiaohongshu.com/explore/afadcdaa4f998d82281ebe5e` | `afadcdaa4f998d82281ebe5e` | `afadcdaa4f998d82281ebe5e` | ✓ |
| 39 | `https://www.xiaohongshu.com/explore/098a7fc57481c940fc5d3941` | `098a7fc57481c940fc5d3941` | `098a7fc57481c940fc5d3941` | ✓ |
| 40 | `https://www.xiaohongshu.com/explore/2d9363fa4524ad802e040598...` | `2d9363fa4524ad802e040598` | `2d9363fa4524ad802e040598` | ✓ |
| 41 | `https://www.xiaohongshu.com/explore/700dd73c65faa828f66225e8...` | `700dd73c65faa828f66225e8` | `700dd73c65faa828f66225e8` | ✓ |
| 42 | `https://www.xiaohongshu.com/explore/b94336eb726b0aebefc883e5...` | `b94336eb726b0aebefc883e5` | `b94336eb726b0aebefc883e5` | ✓ |
| 43 | `https://www.xiaohongshu.com/explore/2ae78d4e32ffbe402b2f91b9` | `2ae78d4e32ffbe402b2f91b9` | `2ae78d4e32ffbe402b2f91b9` | ✓ |
| 44 | `https://www.xiaohongshu.com/explore/ae5dbdb9b95d38b0e95901e6...` | `ae5dbdb9b95d38b0e95901e6` | `ae5dbdb9b95d38b0e95901e6` | ✓ |
| 45 | `https://www.xiaohongshu.com/explore/f95f96f2ce09aa3536a7fdf0` | `f95f96f2ce09aa3536a7fdf0` | `f95f96f2ce09aa3536a7fdf0` | ✓ |
| 46 | `https://www.xiaohongshu.com/explore/95ab0c0addd61645bf96c6ef...` | `95ab0c0addd61645bf96c6ef` | `95ab0c0addd61645bf96c6ef` | ✓ |
| 47 | `https://www.xiaohongshu.com/explore/397493a3d170d84358595ded...` | `397493a3d170d84358595ded` | `397493a3d170d84358595ded` | ✓ |
| 48 | `https://www.xiaohongshu.com/explore/f89dee096573f3d8d81ca838...` | `f89dee096573f3d8d81ca838` | `f89dee096573f3d8d81ca838` | ✓ |
| 49 | `https://www.xiaohongshu.com/explore/e2d8291928d8dc94c79440d4...` | `e2d8291928d8dc94c79440d4` | `e2d8291928d8dc94c79440d4` | ✓ |
| 50 | `https://www.xiaohongshu.com/explore/8bf20d8627fe0f7ccc876af5...` | `8bf20d8627fe0f7ccc876af5` | `8bf20d8627fe0f7ccc876af5` | ✓ |
| 51 | `https://www.xiaohongshu.com/explore/a30233062b934fccf9b9cd80...` | `a30233062b934fccf9b9cd80` | `a30233062b934fccf9b9cd80` | ✓ |
| 52 | `https://www.xiaohongshu.com/explore/0bf2403a0cbddf8d8b9d7a2e` | `0bf2403a0cbddf8d8b9d7a2e` | `0bf2403a0cbddf8d8b9d7a2e` | ✓ |
| 53 | `https://www.xiaohongshu.com/explore/9322d4665b7454addfa05c39...` | `9322d4665b7454addfa05c39` | `9322d4665b7454addfa05c39` | ✓ |
| 54 | `https://www.xiaohongshu.com/explore/f1ba203ec72bd9ca0117ae3d...` | `f1ba203ec72bd9ca0117ae3d` | `f1ba203ec72bd9ca0117ae3d` | ✓ |
| 55 | `https://www.xiaohongshu.com/explore/4c4acc0f7a2d8c565e2abd04...` | `4c4acc0f7a2d8c565e2abd04` | `4c4acc0f7a2d8c565e2abd04` | ✓ |
| 56 | `https://www.xiaohongshu.com/explore/2b32ab3c06aa6426474f86b2...` | `2b32ab3c06aa6426474f86b2` | `2b32ab3c06aa6426474f86b2` | ✓ |
| 57 | `https://www.xiaohongshu.com/explore/7988de2b67bb5ee5406fcf88...` | `7988de2b67bb5ee5406fcf88` | `7988de2b67bb5ee5406fcf88` | ✓ |
| 58 | `https://www.xiaohongshu.com/explore/5316fd56ca91ceff64840f7c...` | `5316fd56ca91ceff64840f7c` | `5316fd56ca91ceff64840f7c` | ✓ |
| 59 | `https://www.xiaohongshu.com/explore/19769fdb31e32d787ed4a873...` | `19769fdb31e32d787ed4a873` | `19769fdb31e32d787ed4a873` | ✓ |
| 60 | `https://www.xiaohongshu.com/explore/39f7211dfef4c2ced095a119...` | `39f7211dfef4c2ced095a119` | `39f7211dfef4c2ced095a119` | ✓ |
| 61 | `https://www.xiaohongshu.com/explore/d7fb945ff2237afb0d9252d3...` | `d7fb945ff2237afb0d9252d3` | `d7fb945ff2237afb0d9252d3` | ✓ |
| 62 | `https://www.xiaohongshu.com/explore/3ccafde1eccfefda7ec16e1e...` | `3ccafde1eccfefda7ec16e1e` | `3ccafde1eccfefda7ec16e1e` | ✓ |
| 63 | `https://www.xiaohongshu.com/explore/4e608257128d5e207dd381b1...` | `4e608257128d5e207dd381b1` | `4e608257128d5e207dd381b1` | ✓ |
| 64 | `https://www.xiaohongshu.com/explore/090e31442f4e8fe04256cfab...` | `090e31442f4e8fe04256cfab` | `090e31442f4e8fe04256cfab` | ✓ |
| 65 | `https://www.xiaohongshu.com/explore/77d1efdd2e169180677b37ee...` | `77d1efdd2e169180677b37ee` | `77d1efdd2e169180677b37ee` | ✓ |
| 66 | `https://www.xiaohongshu.com/explore/8855617c42c79bd699adcccb...` | `8855617c42c79bd699adcccb` | `8855617c42c79bd699adcccb` | ✓ |
| 67 | `https://www.xiaohongshu.com/explore/e660692a7213b44956138694...` | `e660692a7213b44956138694` | `e660692a7213b44956138694` | ✓ |
| 68 | `https://www.xiaohongshu.com/explore/87eebef4a7843d6ed2c16de3...` | `87eebef4a7843d6ed2c16de3` | `87eebef4a7843d6ed2c16de3` | ✓ |
| 69 | `https://www.xiaohongshu.com/explore/6bed00df68dd8f8764dca928...` | `6bed00df68dd8f8764dca928` | `6bed00df68dd8f8764dca928` | ✓ |
| 70 | `https://www.xiaohongshu.com/explore/2b4f09941fbcd81a2de81bbc...` | `2b4f09941fbcd81a2de81bbc` | `2b4f09941fbcd81a2de81bbc` | ✓ |
| 71 | `https://www.xiaohongshu.com/explore/516fe35dd4620f107f8932be...` | `516fe35dd4620f107f8932be` | `516fe35dd4620f107f8932be` | ✓ |
| 72 | `https://www.xiaohongshu.com/explore/bc007385480f5b4048a27f82...` | `bc007385480f5b4048a27f82` | `bc007385480f5b4048a27f82` | ✓ |
| 73 | `https://www.xiaohongshu.com/explore/137701c5b49908cc005e5dc5...` | `137701c5b49908cc005e5dc5` | `137701c5b49908cc005e5dc5` | ✓ |
| 74 | `https://www.xiaohongshu.com/explore/6c713e12de06a715290c1b91...` | `6c713e12de06a715290c1b91` | `6c713e12de06a715290c1b91` | ✓ |
| 75 | `https://www.xiaohongshu.com/explore/da4154e7759d022517172ea9...` | `da4154e7759d022517172ea9` | `da4154e7759d022517172ea9` | ✓ |
| 76 | `https://www.xiaohongshu.com/explore/4a547b017dbd8d3e9c532c15` | `4a547b017dbd8d3e9c532c15` | `4a547b017dbd8d3e9c532c15` | ✓ |
| 77 | `https://www.xiaohongshu.com/explore/2f91c51ebafc5f0347a4eff0...` | `2f91c51ebafc5f0347a4eff0` | `2f91c51ebafc5f0347a4eff0` | ✓ |
| 78 | `https://www.xiaohongshu.com/explore/362a2d7ba9947147f5dac664...` | `362a2d7ba9947147f5dac664` | `362a2d7ba9947147f5dac664` | ✓ |
| 79 | `https://www.xiaohongshu.com/explore/5579d4aea25439dec2a5a482...` | `5579d4aea25439dec2a5a482` | `5579d4aea25439dec2a5a482` | ✓ |
| 80 | `https://www.xiaohongshu.com/explore/92af5e7ac32ec2c1cb8dc482...` | `92af5e7ac32ec2c1cb8dc482` | `92af5e7ac32ec2c1cb8dc482` | ✓ |
| 81 | `https://www.xiaohongshu.com/explore/5ea39e1a9895912b557c1e93...` | `5ea39e1a9895912b557c1e93` | `5ea39e1a9895912b557c1e93` | ✓ |
| 82 | `https://www.xiaohongshu.com/explore/64fd80c35d4ea330c34c790b` | `64fd80c35d4ea330c34c790b` | `64fd80c35d4ea330c34c790b` | ✓ |
| 83 | `https://www.xiaohongshu.com/explore/7ff356001305f7ad70f64ba2` | `7ff356001305f7ad70f64ba2` | `7ff356001305f7ad70f64ba2` | ✓ |
| 84 | `https://www.xiaohongshu.com/explore/789038b80638545e13053ee3...` | `789038b80638545e13053ee3` | `789038b80638545e13053ee3` | ✓ |
| 85 | `https://www.xiaohongshu.com/explore/19a2c3d18474e18e129b3075...` | `19a2c3d18474e18e129b3075` | `19a2c3d18474e18e129b3075` | ✓ |
| 86 | `https://www.xiaohongshu.com/explore/f1821f544974c2d5dcfd961d...` | `f1821f544974c2d5dcfd961d` | `f1821f544974c2d5dcfd961d` | ✓ |
| 87 | `https://www.xiaohongshu.com/explore/f5a6bc4b9303423bf6f16b2a...` | `f5a6bc4b9303423bf6f16b2a` | `f5a6bc4b9303423bf6f16b2a` | ✓ |
| 88 | `https://www.xiaohongshu.com/explore/fe4259ffbc87f2fe04966d31...` | `fe4259ffbc87f2fe04966d31` | `fe4259ffbc87f2fe04966d31` | ✓ |
| 89 | `https://www.xiaohongshu.com/explore/09e58caa452af955ccb9819f...` | `09e58caa452af955ccb9819f` | `09e58caa452af955ccb9819f` | ✓ |
| 90 | `https://www.xiaohongshu.com/explore/4ebf0cdc73891ea70ad5eaee` | `4ebf0cdc73891ea70ad5eaee` | `4ebf0cdc73891ea70ad5eaee` | ✓ |
| 91 | `https://www.xiaohongshu.com/explore/def61177481cb16b69c5aa3f...` | `def61177481cb16b69c5aa3f` | `def61177481cb16b69c5aa3f` | ✓ |
| 92 | `https://www.xiaohongshu.com/explore/941eefac46ded94ceb8fb402...` | `941eefac46ded94ceb8fb402` | `941eefac46ded94ceb8fb402` | ✓ |
| 93 | `https://www.xiaohongshu.com/explore/603a621c3a2d68d135ff3937...` | `603a621c3a2d68d135ff3937` | `603a621c3a2d68d135ff3937` | ✓ |
| 94 | `https://www.xiaohongshu.com/explore/37c00c03f3cb58a86afa93b6...` | `37c00c03f3cb58a86afa93b6` | `37c00c03f3cb58a86afa93b6` | ✓ |
| 95 | `https://www.xiaohongshu.com/explore/67100904e985dfaf3d137f62` | `67100904e985dfaf3d137f62` | `67100904e985dfaf3d137f62` | ✓ |
| 96 | `https://www.xiaohongshu.com/explore/bb229039b7722d2fcdef4800...` | `bb229039b7722d2fcdef4800` | `bb229039b7722d2fcdef4800` | ✓ |
| 97 | `https://www.xiaohongshu.com/explore/2c4fc5091225194103e51a14...` | `2c4fc5091225194103e51a14` | `2c4fc5091225194103e51a14` | ✓ |
| 98 | `https://www.xiaohongshu.com/explore/51ce8aa7ce34e11d22b53dfb...` | `51ce8aa7ce34e11d22b53dfb` | `51ce8aa7ce34e11d22b53dfb` | ✓ |
| 99 | `https://www.xiaohongshu.com/explore/138a5b1702781ecebcb26427...` | `138a5b1702781ecebcb26427` | `138a5b1702781ecebcb26427` | ✓ |
| 100 | `https://www.xiaohongshu.com/explore/5038b4169c737a1111a840c2...` | `5038b4169c737a1111a840c2` | `5038b4169c737a1111a840c2` | ✓ |
| 101 | `https://www.xiaohongshu.com/explore/c7060aae2b724196e203e186` | `c7060aae2b724196e203e186` | `c7060aae2b724196e203e186` | ✓ |
| 102 | `https://www.xiaohongshu.com/explore/19e306e4f2e58f1a5ec8e693...` | `19e306e4f2e58f1a5ec8e693` | `19e306e4f2e58f1a5ec8e693` | ✓ |
| 103 | `https://www.xiaohongshu.com/explore/6b6c3057d95cc445ae4c6e1a` | `6b6c3057d95cc445ae4c6e1a` | `6b6c3057d95cc445ae4c6e1a` | ✓ |
| 104 | `https://www.xiaohongshu.com/explore/a6feaa51c1482c7845a34c1a...` | `a6feaa51c1482c7845a34c1a` | `a6feaa51c1482c7845a34c1a` | ✓ |
| 105 | `https://www.xiaohongshu.com/explore/d522e74da722055ff831278c...` | `d522e74da722055ff831278c` | `d522e74da722055ff831278c` | ✓ |
| 106 | `https://www.xiaohongshu.com/explore/522bc20a0bee434ba94c5cd0...` | `522bc20a0bee434ba94c5cd0` | `522bc20a0bee434ba94c5cd0` | ✓ |
| 107 | `https://www.xiaohongshu.com/explore/15ef9f828d020452c65ed9d0...` | `15ef9f828d020452c65ed9d0` | `15ef9f828d020452c65ed9d0` | ✓ |
| 108 | `https://www.xiaohongshu.com/explore/90a416140d951991de50466f...` | `90a416140d951991de50466f` | `90a416140d951991de50466f` | ✓ |
| 109 | `https://www.xiaohongshu.com/explore/49df00f0122c2103d1d40003...` | `49df00f0122c2103d1d40003` | `49df00f0122c2103d1d40003` | ✓ |
| 110 | `https://www.xiaohongshu.com/explore/7eb115286a102622646889e1...` | `7eb115286a102622646889e1` | `7eb115286a102622646889e1` | ✓ |
| 111 | `https://www.xiaohongshu.com/explore/c6cb5e5cd79873ebb72b2897...` | `c6cb5e5cd79873ebb72b2897` | `c6cb5e5cd79873ebb72b2897` | ✓ |
| 112 | `https://www.xiaohongshu.com/explore/6e637484292beb38580d72ce...` | `6e637484292beb38580d72ce` | `6e637484292beb38580d72ce` | ✓ |
| 113 | `https://www.xiaohongshu.com/explore/bb7fd6a34d2d3408732f336e` | `bb7fd6a34d2d3408732f336e` | `bb7fd6a34d2d3408732f336e` | ✓ |
| 114 | `https://www.xiaohongshu.com/explore/c43e22f59866c54002f49ca1` | `c43e22f59866c54002f49ca1` | `c43e22f59866c54002f49ca1` | ✓ |
| 115 | `https://www.xiaohongshu.com/explore/a062fddafd005fa78f67b77b...` | `a062fddafd005fa78f67b77b` | `a062fddafd005fa78f67b77b` | ✓ |
| 116 | `https://www.xiaohongshu.com/explore/6972a7e13442f0b26a462026...` | `6972a7e13442f0b26a462026` | `6972a7e13442f0b26a462026` | ✓ |
| 117 | `https://www.xiaohongshu.com/explore/235091c253213ca5940220c0...` | `235091c253213ca5940220c0` | `235091c253213ca5940220c0` | ✓ |
| 118 | `https://www.xiaohongshu.com/explore/6d775b65d00812e3c4f20a72...` | `6d775b65d00812e3c4f20a72` | `6d775b65d00812e3c4f20a72` | ✓ |
| 119 | `https://www.xiaohongshu.com/explore/378caeeedae4f4ba56277282...` | `378caeeedae4f4ba56277282` | `378caeeedae4f4ba56277282` | ✓ |
| 120 | `https://www.xiaohongshu.com/explore/69fc973d50924a91ca2180a0...` | `69fc973d50924a91ca2180a0` | `69fc973d50924a91ca2180a0` | ✓ |
| 121 | `https://www.xiaohongshu.com/explore/05916af8c5f928ea887e6f2f...` | `05916af8c5f928ea887e6f2f` | `05916af8c5f928ea887e6f2f` | ✓ |
| 122 | `https://www.xiaohongshu.com/explore/389c83d1982d18e2e2bca183...` | `389c83d1982d18e2e2bca183` | `389c83d1982d18e2e2bca183` | ✓ |
| 123 | `https://www.xiaohongshu.com/explore/88a7180afa3c3cd9a36b28d3` | `88a7180afa3c3cd9a36b28d3` | `88a7180afa3c3cd9a36b28d3` | ✓ |
| 124 | `https://www.xiaohongshu.com/explore/aa08742d24f82739ced29f9b...` | `aa08742d24f82739ced29f9b` | `aa08742d24f82739ced29f9b` | ✓ |
| 125 | `https://www.xiaohongshu.com/explore/e67161867349b1f36252d974...` | `e67161867349b1f36252d974` | `e67161867349b1f36252d974` | ✓ |
| 126 | `https://www.xiaohongshu.com/explore/a73f54e6a0812bd7d4a42841...` | `a73f54e6a0812bd7d4a42841` | `a73f54e6a0812bd7d4a42841` | ✓ |
| 127 | `https://www.xiaohongshu.com/explore/40de1d9e9ac28eb9cb087ef7...` | `40de1d9e9ac28eb9cb087ef7` | `40de1d9e9ac28eb9cb087ef7` | ✓ |
| 128 | `https://www.xiaohongshu.com/explore/37ecc5f9bb7cd1a3c5ca7f9f...` | `37ecc5f9bb7cd1a3c5ca7f9f` | `37ecc5f9bb7cd1a3c5ca7f9f` | ✓ |
| 129 | `https://www.xiaohongshu.com/explore/607b7becc04b48756f7d8da5...` | `607b7becc04b48756f7d8da5` | `607b7becc04b48756f7d8da5` | ✓ |
| 130 | `https://www.xiaohongshu.com/explore/5393caabfa3937eb50fa1eb9` | `5393caabfa3937eb50fa1eb9` | `5393caabfa3937eb50fa1eb9` | ✓ |
| 131 | `https://www.xiaohongshu.com/explore/330025c62967ef04834c53b6...` | `330025c62967ef04834c53b6` | `330025c62967ef04834c53b6` | ✓ |
| 132 | `https://www.xiaohongshu.com/explore/b8a5b6f10fc90bd8123c8ef5...` | `b8a5b6f10fc90bd8123c8ef5` | `b8a5b6f10fc90bd8123c8ef5` | ✓ |
| 133 | `https://www.xiaohongshu.com/explore/426f533a9b33c8aa39908674` | `426f533a9b33c8aa39908674` | `426f533a9b33c8aa39908674` | ✓ |
| 134 | `https://www.xiaohongshu.com/explore/e73762c1526296a472cd0e43...` | `e73762c1526296a472cd0e43` | `e73762c1526296a472cd0e43` | ✓ |
| 135 | `https://www.xiaohongshu.com/explore/40ae0128223344e74bca8a31...` | `40ae0128223344e74bca8a31` | `40ae0128223344e74bca8a31` | ✓ |
| 136 | `https://www.xiaohongshu.com/explore/e900f2e0ee51d61ced47ba7f...` | `e900f2e0ee51d61ced47ba7f` | `e900f2e0ee51d61ced47ba7f` | ✓ |
| 137 | `https://www.xiaohongshu.com/explore/1e6a04fceae6eeaf229999b8...` | `1e6a04fceae6eeaf229999b8` | `1e6a04fceae6eeaf229999b8` | ✓ |
| 138 | `https://www.xiaohongshu.com/explore/40a1ff334da3b1cd8dd44a6f...` | `40a1ff334da3b1cd8dd44a6f` | `40a1ff334da3b1cd8dd44a6f` | ✓ |
| 139 | `https://www.xiaohongshu.com/explore/8247af638d02ceb98974976c...` | `8247af638d02ceb98974976c` | `8247af638d02ceb98974976c` | ✓ |
| 140 | `https://www.xiaohongshu.com/explore/40cfdb793973ca3dac389a64...` | `40cfdb793973ca3dac389a64` | `40cfdb793973ca3dac389a64` | ✓ |
| 141 | `https://www.xiaohongshu.com/explore/58163885614f08d5a1d61ba4...` | `58163885614f08d5a1d61ba4` | `58163885614f08d5a1d61ba4` | ✓ |
| 142 | `https://www.xiaohongshu.com/explore/355103bb8e6039197242fe10...` | `355103bb8e6039197242fe10` | `355103bb8e6039197242fe10` | ✓ |
| 143 | `https://www.xiaohongshu.com/explore/b05a39fca0714c10e9b42439...` | `b05a39fca0714c10e9b42439` | `b05a39fca0714c10e9b42439` | ✓ |
| 144 | `https://www.xiaohongshu.com/explore/5089525db1b70f104f42fcfd` | `5089525db1b70f104f42fcfd` | `5089525db1b70f104f42fcfd` | ✓ |
| 145 | `https://www.xiaohongshu.com/explore/66582e16c233edc3a9e2a69a...` | `66582e16c233edc3a9e2a69a` | `66582e16c233edc3a9e2a69a` | ✓ |
| 146 | `https://www.xiaohongshu.com/explore/c47c5ec93e6036966fffbb70` | `c47c5ec93e6036966fffbb70` | `c47c5ec93e6036966fffbb70` | ✓ |
| 147 | `https://www.xiaohongshu.com/explore/d1179cf0763cb1f08ea339c5...` | `d1179cf0763cb1f08ea339c5` | `d1179cf0763cb1f08ea339c5` | ✓ |
| 148 | `https://www.xiaohongshu.com/explore/ffadd2468bb0e2be2c5950f7...` | `ffadd2468bb0e2be2c5950f7` | `ffadd2468bb0e2be2c5950f7` | ✓ |
| 149 | `https://www.xiaohongshu.com/explore/b6d74561625384b436bc7f28` | `b6d74561625384b436bc7f28` | `b6d74561625384b436bc7f28` | ✓ |
| 150 | `https://www.xiaohongshu.com/explore/f115bb48dd68c975ca4bc53b...` | `f115bb48dd68c975ca4bc53b` | `f115bb48dd68c975ca4bc53b` | ✓ |

### discovery 类型

> 旧版 discovery/item 格式链接
>
> 共 100 个测试案例

| # | URL | 期望ID | 实际ID | 结果 |
|---|-----|--------|--------|------|
| 1 | `https://www.xiaohongshu.com/discovery/item/8da0d2c1f26983be7...` | `8da0d2c1f26983be720a83dc` | `8da0d2c1f26983be720a83dc` | ✓ |
| 2 | `https://www.xiaohongshu.com/discovery/item/452ca8ade4b767b34...` | `452ca8ade4b767b344125eb4` | `452ca8ade4b767b344125eb4` | ✓ |
| 3 | `https://www.xiaohongshu.com/discovery/item/b74497a947b0fa50b...` | `b74497a947b0fa50b50fd121` | `b74497a947b0fa50b50fd121` | ✓ |
| 4 | `https://www.xiaohongshu.com/discovery/item/da7e8b4230d57b694...` | `da7e8b4230d57b694675f20e` | `da7e8b4230d57b694675f20e` | ✓ |
| 5 | `https://www.xiaohongshu.com/discovery/item/6198a56fb1d01f654...` | `6198a56fb1d01f65401342ee` | `6198a56fb1d01f65401342ee` | ✓ |
| 6 | `https://www.xiaohongshu.com/discovery/item/6b3575ca60db0ea7d...` | `6b3575ca60db0ea7d8c717e2` | `6b3575ca60db0ea7d8c717e2` | ✓ |
| 7 | `https://www.xiaohongshu.com/discovery/item/7b1808909e47a8f03...` | `7b1808909e47a8f03c11f76f` | `7b1808909e47a8f03c11f76f` | ✓ |
| 8 | `https://www.xiaohongshu.com/discovery/item/517fe55b6836afe7e...` | `517fe55b6836afe7ede35094` | `517fe55b6836afe7ede35094` | ✓ |
| 9 | `https://www.xiaohongshu.com/discovery/item/fe878011e2c99fc87...` | `fe878011e2c99fc8753a0c3e` | `fe878011e2c99fc8753a0c3e` | ✓ |
| 10 | `https://www.xiaohongshu.com/discovery/item/163d43f487fcd1767...` | `163d43f487fcd176796414af` | `163d43f487fcd176796414af` | ✓ |
| 11 | `https://www.xiaohongshu.com/discovery/item/de6bdead844cf3b7e...` | `de6bdead844cf3b7e3138051` | `de6bdead844cf3b7e3138051` | ✓ |
| 12 | `https://www.xiaohongshu.com/discovery/item/8e8b2c99ce6c9cd96...` | `8e8b2c99ce6c9cd960a655d5` | `8e8b2c99ce6c9cd960a655d5` | ✓ |
| 13 | `https://www.xiaohongshu.com/discovery/item/b64dbf5522144c4e9...` | `b64dbf5522144c4e9ec10275` | `b64dbf5522144c4e9ec10275` | ✓ |
| 14 | `https://www.xiaohongshu.com/discovery/item/7cc75071006e0b36b...` | `7cc75071006e0b36b39c9543` | `7cc75071006e0b36b39c9543` | ✓ |
| 15 | `https://www.xiaohongshu.com/discovery/item/45aae315b6d6ee86d...` | `45aae315b6d6ee86d4a6010d` | `45aae315b6d6ee86d4a6010d` | ✓ |
| 16 | `https://www.xiaohongshu.com/discovery/item/c47e43b614eb2b6cc...` | `c47e43b614eb2b6ccd9bfb69` | `c47e43b614eb2b6ccd9bfb69` | ✓ |
| 17 | `https://www.xiaohongshu.com/discovery/item/8383cfc0ba7608a21...` | `8383cfc0ba7608a21aadcf92` | `8383cfc0ba7608a21aadcf92` | ✓ |
| 18 | `https://www.xiaohongshu.com/discovery/item/95340539ef51e848b...` | `95340539ef51e848b4a55a58` | `95340539ef51e848b4a55a58` | ✓ |
| 19 | `https://www.xiaohongshu.com/discovery/item/fd9bfbbda525c7288...` | `fd9bfbbda525c7288c5f9163` | `fd9bfbbda525c7288c5f9163` | ✓ |
| 20 | `https://www.xiaohongshu.com/discovery/item/8a032a9520a8a77e9...` | `8a032a9520a8a77e951a09c5` | `8a032a9520a8a77e951a09c5` | ✓ |
| 21 | `https://www.xiaohongshu.com/discovery/item/7cf1541cb26e19713...` | `7cf1541cb26e197139eb2a44` | `7cf1541cb26e197139eb2a44` | ✓ |
| 22 | `https://www.xiaohongshu.com/discovery/item/0364d80c814a8539b...` | `0364d80c814a8539b9752ff8` | `0364d80c814a8539b9752ff8` | ✓ |
| 23 | `https://www.xiaohongshu.com/discovery/item/ff26f6d99ef5acf1f...` | `ff26f6d99ef5acf1f88eefb1` | `ff26f6d99ef5acf1f88eefb1` | ✓ |
| 24 | `https://www.xiaohongshu.com/discovery/item/0a2b85f877c22bfd3...` | `0a2b85f877c22bfd37ad3613` | `0a2b85f877c22bfd37ad3613` | ✓ |
| 25 | `https://www.xiaohongshu.com/discovery/item/f58251791ab9eaf24...` | `f58251791ab9eaf248a56e7a` | `f58251791ab9eaf248a56e7a` | ✓ |
| 26 | `https://www.xiaohongshu.com/discovery/item/99dd49b004babd8f3...` | `99dd49b004babd8f32856639` | `99dd49b004babd8f32856639` | ✓ |
| 27 | `https://www.xiaohongshu.com/discovery/item/91ec62aa4262bc0c9...` | `91ec62aa4262bc0c998ff0b8` | `91ec62aa4262bc0c998ff0b8` | ✓ |
| 28 | `https://www.xiaohongshu.com/discovery/item/cc663361a441b6fbd...` | `cc663361a441b6fbd64559c2` | `cc663361a441b6fbd64559c2` | ✓ |
| 29 | `https://www.xiaohongshu.com/discovery/item/cc5a89124bc8f1168...` | `cc5a89124bc8f116809af18b` | `cc5a89124bc8f116809af18b` | ✓ |
| 30 | `https://www.xiaohongshu.com/discovery/item/425b6601111145feb...` | `425b6601111145febc92af97` | `425b6601111145febc92af97` | ✓ |
| 31 | `https://www.xiaohongshu.com/discovery/item/dd86d0b9404960af2...` | `dd86d0b9404960af23cc3c40` | `dd86d0b9404960af23cc3c40` | ✓ |
| 32 | `https://www.xiaohongshu.com/discovery/item/32a478632e51fe3f1...` | `32a478632e51fe3f1c192847` | `32a478632e51fe3f1c192847` | ✓ |
| 33 | `https://www.xiaohongshu.com/discovery/item/52b7452ade388a47d...` | `52b7452ade388a47dfb286ad` | `52b7452ade388a47dfb286ad` | ✓ |
| 34 | `https://www.xiaohongshu.com/discovery/item/d13f1d9055350c40d...` | `d13f1d9055350c40d5eba3d0` | `d13f1d9055350c40d5eba3d0` | ✓ |
| 35 | `https://www.xiaohongshu.com/discovery/item/20004652583770c32...` | `20004652583770c324316078` | `20004652583770c324316078` | ✓ |
| 36 | `https://www.xiaohongshu.com/discovery/item/1588b8b08fc1f519b...` | `1588b8b08fc1f519b24e9143` | `1588b8b08fc1f519b24e9143` | ✓ |
| 37 | `https://www.xiaohongshu.com/discovery/item/08658eb8e56139fc4...` | `08658eb8e56139fc420119d6` | `08658eb8e56139fc420119d6` | ✓ |
| 38 | `https://www.xiaohongshu.com/discovery/item/d2e2082a8fd5994fb...` | `d2e2082a8fd5994fb898fcbc` | `d2e2082a8fd5994fb898fcbc` | ✓ |
| 39 | `https://www.xiaohongshu.com/discovery/item/7d73a0558024010ec...` | `7d73a0558024010ec32db6c2` | `7d73a0558024010ec32db6c2` | ✓ |
| 40 | `https://www.xiaohongshu.com/discovery/item/2bf92e29d17c567bd...` | `2bf92e29d17c567bdbfa9eed` | `2bf92e29d17c567bdbfa9eed` | ✓ |
| 41 | `https://www.xiaohongshu.com/discovery/item/ddda545304620c24b...` | `ddda545304620c24b90d2bc0` | `ddda545304620c24b90d2bc0` | ✓ |
| 42 | `https://www.xiaohongshu.com/discovery/item/d9a82211756fbc1d2...` | `d9a82211756fbc1d2fa8ba43` | `d9a82211756fbc1d2fa8ba43` | ✓ |
| 43 | `https://www.xiaohongshu.com/discovery/item/c4e58ce19ea2f5915...` | `c4e58ce19ea2f59156f5fd32` | `c4e58ce19ea2f59156f5fd32` | ✓ |
| 44 | `https://www.xiaohongshu.com/discovery/item/40802acd8844dc927...` | `40802acd8844dc9273d09481` | `40802acd8844dc9273d09481` | ✓ |
| 45 | `https://www.xiaohongshu.com/discovery/item/8b970a2410a54bd59...` | `8b970a2410a54bd597d43201` | `8b970a2410a54bd597d43201` | ✓ |
| 46 | `https://www.xiaohongshu.com/discovery/item/b541ad77d003fde80...` | `b541ad77d003fde803074010` | `b541ad77d003fde803074010` | ✓ |
| 47 | `https://www.xiaohongshu.com/discovery/item/e23a28e05b6f5ea4c...` | `e23a28e05b6f5ea4cb947072` | `e23a28e05b6f5ea4cb947072` | ✓ |
| 48 | `https://www.xiaohongshu.com/discovery/item/0231940939e65ed17...` | `0231940939e65ed17fc95225` | `0231940939e65ed17fc95225` | ✓ |
| 49 | `https://www.xiaohongshu.com/discovery/item/71d163fed21d0ea34...` | `71d163fed21d0ea342e69554` | `71d163fed21d0ea342e69554` | ✓ |
| 50 | `https://www.xiaohongshu.com/discovery/item/18457094801be5b27...` | `18457094801be5b270a80bab` | `18457094801be5b270a80bab` | ✓ |
| 51 | `https://www.xiaohongshu.com/discovery/item/66cb5afddb18bbf1e...` | `66cb5afddb18bbf1e1e62b53` | `66cb5afddb18bbf1e1e62b53` | ✓ |
| 52 | `https://www.xiaohongshu.com/discovery/item/95ad8273a8e0ba34a...` | `95ad8273a8e0ba34a9e8d02d` | `95ad8273a8e0ba34a9e8d02d` | ✓ |
| 53 | `https://www.xiaohongshu.com/discovery/item/126ab33fe34ed35af...` | `126ab33fe34ed35afa643089` | `126ab33fe34ed35afa643089` | ✓ |
| 54 | `https://www.xiaohongshu.com/discovery/item/f2ca4d2ce7a9811a7...` | `f2ca4d2ce7a9811a76ec1894` | `f2ca4d2ce7a9811a76ec1894` | ✓ |
| 55 | `https://www.xiaohongshu.com/discovery/item/1af6871f49ebf4a99...` | `1af6871f49ebf4a99368bb0d` | `1af6871f49ebf4a99368bb0d` | ✓ |
| 56 | `https://www.xiaohongshu.com/discovery/item/ae29f43277713fc4c...` | `ae29f43277713fc4cde41047` | `ae29f43277713fc4cde41047` | ✓ |
| 57 | `https://www.xiaohongshu.com/discovery/item/1adab43337391017c...` | `1adab43337391017cc2f245b` | `1adab43337391017cc2f245b` | ✓ |
| 58 | `https://www.xiaohongshu.com/discovery/item/e79f2af85b0659f57...` | `e79f2af85b0659f57a86d5ff` | `e79f2af85b0659f57a86d5ff` | ✓ |
| 59 | `https://www.xiaohongshu.com/discovery/item/feee58f3acaa743d2...` | `feee58f3acaa743d2b1edb96` | `feee58f3acaa743d2b1edb96` | ✓ |
| 60 | `https://www.xiaohongshu.com/discovery/item/93243de7712c3a667...` | `93243de7712c3a667ef43f2b` | `93243de7712c3a667ef43f2b` | ✓ |
| 61 | `https://www.xiaohongshu.com/discovery/item/1357498402f9414ea...` | `1357498402f9414ea61bef8d` | `1357498402f9414ea61bef8d` | ✓ |
| 62 | `https://www.xiaohongshu.com/discovery/item/0fb7c6dae4e16ba6c...` | `0fb7c6dae4e16ba6c36901ff` | `0fb7c6dae4e16ba6c36901ff` | ✓ |
| 63 | `https://www.xiaohongshu.com/discovery/item/0bdd2c023938f21c1...` | `0bdd2c023938f21c1cb1e1ec` | `0bdd2c023938f21c1cb1e1ec` | ✓ |
| 64 | `https://www.xiaohongshu.com/discovery/item/f923afab9751c9e40...` | `f923afab9751c9e406964a6c` | `f923afab9751c9e406964a6c` | ✓ |
| 65 | `https://www.xiaohongshu.com/discovery/item/fcbb0c38b2000f612...` | `fcbb0c38b2000f612ac172dc` | `fcbb0c38b2000f612ac172dc` | ✓ |
| 66 | `https://www.xiaohongshu.com/discovery/item/282a91bf4280095df...` | `282a91bf4280095dff703e44` | `282a91bf4280095dff703e44` | ✓ |
| 67 | `https://www.xiaohongshu.com/discovery/item/a16f57c7122a6c339...` | `a16f57c7122a6c339feda857` | `a16f57c7122a6c339feda857` | ✓ |
| 68 | `https://www.xiaohongshu.com/discovery/item/37376540caa130a01...` | `37376540caa130a019653229` | `37376540caa130a019653229` | ✓ |
| 69 | `https://www.xiaohongshu.com/discovery/item/f913122fa03daac32...` | `f913122fa03daac32f8d28bd` | `f913122fa03daac32f8d28bd` | ✓ |
| 70 | `https://www.xiaohongshu.com/discovery/item/c5ec7cb8af3931073...` | `c5ec7cb8af39310734fac517` | `c5ec7cb8af39310734fac517` | ✓ |
| 71 | `https://www.xiaohongshu.com/discovery/item/f0c653f8b875c101d...` | `f0c653f8b875c101d51cf167` | `f0c653f8b875c101d51cf167` | ✓ |
| 72 | `https://www.xiaohongshu.com/discovery/item/3ee9aae174a98fdd5...` | `3ee9aae174a98fdd5609e406` | `3ee9aae174a98fdd5609e406` | ✓ |
| 73 | `https://www.xiaohongshu.com/discovery/item/4bf5cedc29399e328...` | `4bf5cedc29399e3284ff9e6e` | `4bf5cedc29399e3284ff9e6e` | ✓ |
| 74 | `https://www.xiaohongshu.com/discovery/item/29a0e82254ea25865...` | `29a0e82254ea25865bf828ec` | `29a0e82254ea25865bf828ec` | ✓ |
| 75 | `https://www.xiaohongshu.com/discovery/item/0b7f7350105379380...` | `0b7f7350105379380819d1a8` | `0b7f7350105379380819d1a8` | ✓ |
| 76 | `https://www.xiaohongshu.com/discovery/item/75816e4606043ba9f...` | `75816e4606043ba9f5ab7eda` | `75816e4606043ba9f5ab7eda` | ✓ |
| 77 | `https://www.xiaohongshu.com/discovery/item/187664b166f077a63...` | `187664b166f077a63a5daf6a` | `187664b166f077a63a5daf6a` | ✓ |
| 78 | `https://www.xiaohongshu.com/discovery/item/456f0fa3e89ac9fc5...` | `456f0fa3e89ac9fc5dcdcf96` | `456f0fa3e89ac9fc5dcdcf96` | ✓ |
| 79 | `https://www.xiaohongshu.com/discovery/item/cdc706c2d7d1ed1b3...` | `cdc706c2d7d1ed1b38ca6a51` | `cdc706c2d7d1ed1b38ca6a51` | ✓ |
| 80 | `https://www.xiaohongshu.com/discovery/item/a7f0b220e20b77de4...` | `a7f0b220e20b77de4a1052a0` | `a7f0b220e20b77de4a1052a0` | ✓ |
| 81 | `https://www.xiaohongshu.com/discovery/item/fe85f04c07a4e6c50...` | `fe85f04c07a4e6c50ba4a39a` | `fe85f04c07a4e6c50ba4a39a` | ✓ |
| 82 | `https://www.xiaohongshu.com/discovery/item/cf64867642bf2ab26...` | `cf64867642bf2ab2685fde04` | `cf64867642bf2ab2685fde04` | ✓ |
| 83 | `https://www.xiaohongshu.com/discovery/item/fd9dae35d9c10d937...` | `fd9dae35d9c10d93799b32e9` | `fd9dae35d9c10d93799b32e9` | ✓ |
| 84 | `https://www.xiaohongshu.com/discovery/item/4dd5a9c023ffe0959...` | `4dd5a9c023ffe0959c7a66d5` | `4dd5a9c023ffe0959c7a66d5` | ✓ |
| 85 | `https://www.xiaohongshu.com/discovery/item/0703c47d0d133f849...` | `0703c47d0d133f849ac426c4` | `0703c47d0d133f849ac426c4` | ✓ |
| 86 | `https://www.xiaohongshu.com/discovery/item/b4212cf0497cd60fc...` | `b4212cf0497cd60fc426f1a8` | `b4212cf0497cd60fc426f1a8` | ✓ |
| 87 | `https://www.xiaohongshu.com/discovery/item/3d204af059d49d37d...` | `3d204af059d49d37de9aba46` | `3d204af059d49d37de9aba46` | ✓ |
| 88 | `https://www.xiaohongshu.com/discovery/item/f09b2b2fa0ddff995...` | `f09b2b2fa0ddff995193663e` | `f09b2b2fa0ddff995193663e` | ✓ |
| 89 | `https://www.xiaohongshu.com/discovery/item/0335366ee58700829...` | `0335366ee587008298b4c951` | `0335366ee587008298b4c951` | ✓ |
| 90 | `https://www.xiaohongshu.com/discovery/item/347d886256a4bddcc...` | `347d886256a4bddcc8b25313` | `347d886256a4bddcc8b25313` | ✓ |
| 91 | `https://www.xiaohongshu.com/discovery/item/01f58a0ba74f53497...` | `01f58a0ba74f534978910268` | `01f58a0ba74f534978910268` | ✓ |
| 92 | `https://www.xiaohongshu.com/discovery/item/49d6ab69b3d549ac9...` | `49d6ab69b3d549ac9c9ef440` | `49d6ab69b3d549ac9c9ef440` | ✓ |
| 93 | `https://www.xiaohongshu.com/discovery/item/835fcdeba1eefc7f7...` | `835fcdeba1eefc7f7824da2f` | `835fcdeba1eefc7f7824da2f` | ✓ |
| 94 | `https://www.xiaohongshu.com/discovery/item/530337566df8e6df1...` | `530337566df8e6df129dd722` | `530337566df8e6df129dd722` | ✓ |
| 95 | `https://www.xiaohongshu.com/discovery/item/1314de4ef431063a1...` | `1314de4ef431063a1d80fde1` | `1314de4ef431063a1d80fde1` | ✓ |
| 96 | `https://www.xiaohongshu.com/discovery/item/11c7dfeb4fbffadd5...` | `11c7dfeb4fbffadd5223e114` | `11c7dfeb4fbffadd5223e114` | ✓ |
| 97 | `https://www.xiaohongshu.com/discovery/item/5514375635ee015b9...` | `5514375635ee015b9ecaaa87` | `5514375635ee015b9ecaaa87` | ✓ |
| 98 | `https://www.xiaohongshu.com/discovery/item/69b7694fec6d2efec...` | `69b7694fec6d2efecfbd74a4` | `69b7694fec6d2efecfbd74a4` | ✓ |
| 99 | `https://www.xiaohongshu.com/discovery/item/2239e066def7d2b50...` | `2239e066def7d2b50fe5a853` | `2239e066def7d2b50fe5a853` | ✓ |
| 100 | `https://www.xiaohongshu.com/discovery/item/6205d25d2c63016e5...` | `6205d25d2c63016e579e3773` | `6205d25d2c63016e579e3773` | ✓ |

### xhslink 类型

> 小红书短链接格式
>
> 共 150 个测试案例

| # | URL | 期望ID | 实际ID | 结果 |
|---|-----|--------|--------|------|
| 1 | `https://xhslink.com/p4BX5bwi` | `p4BX5bwi` | `p4BX5bwi` | ✓ |
| 2 | `https://xhslink.com/kzNlhV8l` | `kzNlhV8l` | `kzNlhV8l` | ✓ |
| 3 | `https://xhslink.com/CZSU0yPW` | `CZSU0yPW` | `CZSU0yPW` | ✓ |
| 4 | `https://xhslink.com/Bltlkryy` | `Bltlkryy` | `Bltlkryy` | ✓ |
| 5 | `https://xhslink.com/Yn8NTLul` | `Yn8NTLul` | `Yn8NTLul` | ✓ |
| 6 | `https://xhslink.com/C5IxaePk` | `C5IxaePk` | `C5IxaePk` | ✓ |
| 7 | `https://xhslink.com/o2Wlz97g` | `o2Wlz97g` | `o2Wlz97g` | ✓ |
| 8 | `https://xhslink.com/KTdms0Vv` | `KTdms0Vv` | `KTdms0Vv` | ✓ |
| 9 | `https://xhslink.com/7LGkQzvX` | `7LGkQzvX` | `7LGkQzvX` | ✓ |
| 10 | `https://xhslink.com/0TuGsrT0` | `0TuGsrT0` | `0TuGsrT0` | ✓ |
| 11 | `https://xhslink.com/ybVwvVFb` | `ybVwvVFb` | `ybVwvVFb` | ✓ |
| 12 | `https://xhslink.com/oOP32Mr3` | `oOP32Mr3` | `oOP32Mr3` | ✓ |
| 13 | `https://xhslink.com/onL4igHY` | `onL4igHY` | `onL4igHY` | ✓ |
| 14 | `https://xhslink.com/A9JQNhwr` | `A9JQNhwr` | `A9JQNhwr` | ✓ |
| 15 | `https://xhslink.com/Fggv7oIt` | `Fggv7oIt` | `Fggv7oIt` | ✓ |
| 16 | `https://xhslink.com/eyhm4Egj` | `eyhm4Egj` | `eyhm4Egj` | ✓ |
| 17 | `https://xhslink.com/Dt2QQnLI` | `Dt2QQnLI` | `Dt2QQnLI` | ✓ |
| 18 | `https://xhslink.com/1JLx1p6d` | `1JLx1p6d` | `1JLx1p6d` | ✓ |
| 19 | `https://xhslink.com/1eUR2RT7` | `1eUR2RT7` | `1eUR2RT7` | ✓ |
| 20 | `https://xhslink.com/iV7y74J9` | `iV7y74J9` | `iV7y74J9` | ✓ |
| 21 | `https://xhslink.com/dkaEiyuv` | `dkaEiyuv` | `dkaEiyuv` | ✓ |
| 22 | `https://xhslink.com/IAYWtGSI` | `IAYWtGSI` | `IAYWtGSI` | ✓ |
| 23 | `https://xhslink.com/IqXgrubO` | `IqXgrubO` | `IqXgrubO` | ✓ |
| 24 | `https://xhslink.com/dfJpZFua` | `dfJpZFua` | `dfJpZFua` | ✓ |
| 25 | `https://xhslink.com/vx10ELL1` | `vx10ELL1` | `vx10ELL1` | ✓ |
| 26 | `https://xhslink.com/tYSQmcWo` | `tYSQmcWo` | `tYSQmcWo` | ✓ |
| 27 | `https://xhslink.com/ULOgdQok` | `ULOgdQok` | `ULOgdQok` | ✓ |
| 28 | `https://xhslink.com/7BHvyThe` | `7BHvyThe` | `7BHvyThe` | ✓ |
| 29 | `https://xhslink.com/CnBf1n5l` | `CnBf1n5l` | `CnBf1n5l` | ✓ |
| 30 | `https://xhslink.com/uuP3zyBP` | `uuP3zyBP` | `uuP3zyBP` | ✓ |
| 31 | `https://xhslink.com/vWF7LKx7` | `vWF7LKx7` | `vWF7LKx7` | ✓ |
| 32 | `https://xhslink.com/4SiAs9RH` | `4SiAs9RH` | `4SiAs9RH` | ✓ |
| 33 | `https://xhslink.com/3rTzm3Rd` | `3rTzm3Rd` | `3rTzm3Rd` | ✓ |
| 34 | `https://xhslink.com/hJgiZfYx` | `hJgiZfYx` | `hJgiZfYx` | ✓ |
| 35 | `https://xhslink.com/1pa1dR3s` | `1pa1dR3s` | `1pa1dR3s` | ✓ |
| 36 | `https://xhslink.com/3qaCKpOD` | `3qaCKpOD` | `3qaCKpOD` | ✓ |
| 37 | `https://xhslink.com/gwxamq0P` | `gwxamq0P` | `gwxamq0P` | ✓ |
| 38 | `https://xhslink.com/pjOrFyXT` | `pjOrFyXT` | `pjOrFyXT` | ✓ |
| 39 | `https://xhslink.com/up0gmLcY` | `up0gmLcY` | `up0gmLcY` | ✓ |
| 40 | `https://xhslink.com/PYDMdtBZ` | `PYDMdtBZ` | `PYDMdtBZ` | ✓ |
| 41 | `https://xhslink.com/NWd060rQ` | `NWd060rQ` | `NWd060rQ` | ✓ |
| 42 | `https://xhslink.com/KBbzSJUG` | `KBbzSJUG` | `KBbzSJUG` | ✓ |
| 43 | `https://xhslink.com/ysoh32e7` | `ysoh32e7` | `ysoh32e7` | ✓ |
| 44 | `https://xhslink.com/4JWllnvn` | `4JWllnvn` | `4JWllnvn` | ✓ |
| 45 | `https://xhslink.com/JdX1lKni` | `JdX1lKni` | `JdX1lKni` | ✓ |
| 46 | `https://xhslink.com/WIeIfShY` | `WIeIfShY` | `WIeIfShY` | ✓ |
| 47 | `https://xhslink.com/sp9ld9mI` | `sp9ld9mI` | `sp9ld9mI` | ✓ |
| 48 | `https://xhslink.com/NoM6Y9f6` | `NoM6Y9f6` | `NoM6Y9f6` | ✓ |
| 49 | `https://xhslink.com/sRsxX79U` | `sRsxX79U` | `sRsxX79U` | ✓ |
| 50 | `https://xhslink.com/T7AZUnWn` | `T7AZUnWn` | `T7AZUnWn` | ✓ |
| 51 | `https://xhslink.com/2P0ELnVg` | `2P0ELnVg` | `2P0ELnVg` | ✓ |
| 52 | `https://xhslink.com/uYtv6vmg` | `uYtv6vmg` | `uYtv6vmg` | ✓ |
| 53 | `https://xhslink.com/C5HooHjy` | `C5HooHjy` | `C5HooHjy` | ✓ |
| 54 | `https://xhslink.com/GXClMHkz` | `GXClMHkz` | `GXClMHkz` | ✓ |
| 55 | `https://xhslink.com/Vo2UDxUG` | `Vo2UDxUG` | `Vo2UDxUG` | ✓ |
| 56 | `https://xhslink.com/X57ihZP2` | `X57ihZP2` | `X57ihZP2` | ✓ |
| 57 | `https://xhslink.com/nvGxd1kf` | `nvGxd1kf` | `nvGxd1kf` | ✓ |
| 58 | `https://xhslink.com/qFpSTbG7` | `qFpSTbG7` | `qFpSTbG7` | ✓ |
| 59 | `https://xhslink.com/gxxeROke` | `gxxeROke` | `gxxeROke` | ✓ |
| 60 | `https://xhslink.com/gKzbZTNT` | `gKzbZTNT` | `gKzbZTNT` | ✓ |
| 61 | `https://xhslink.com/QJmnNMb7` | `QJmnNMb7` | `QJmnNMb7` | ✓ |
| 62 | `https://xhslink.com/jbTg3ZJU` | `jbTg3ZJU` | `jbTg3ZJU` | ✓ |
| 63 | `https://xhslink.com/LpRZ6iTF` | `LpRZ6iTF` | `LpRZ6iTF` | ✓ |
| 64 | `https://xhslink.com/brnr3I7a` | `brnr3I7a` | `brnr3I7a` | ✓ |
| 65 | `https://xhslink.com/v1GEXMBt` | `v1GEXMBt` | `v1GEXMBt` | ✓ |
| 66 | `https://xhslink.com/1MCIIMYy` | `1MCIIMYy` | `1MCIIMYy` | ✓ |
| 67 | `https://xhslink.com/WXrWwnIL` | `WXrWwnIL` | `WXrWwnIL` | ✓ |
| 68 | `https://xhslink.com/7Qj7StMD` | `7Qj7StMD` | `7Qj7StMD` | ✓ |
| 69 | `https://xhslink.com/OSlmfO6Z` | `OSlmfO6Z` | `OSlmfO6Z` | ✓ |
| 70 | `https://xhslink.com/EDNqpLmr` | `EDNqpLmr` | `EDNqpLmr` | ✓ |
| 71 | `https://xhslink.com/V7W59AVG` | `V7W59AVG` | `V7W59AVG` | ✓ |
| 72 | `https://xhslink.com/eOS7J7Bb` | `eOS7J7Bb` | `eOS7J7Bb` | ✓ |
| 73 | `https://xhslink.com/68dlfMpF` | `68dlfMpF` | `68dlfMpF` | ✓ |
| 74 | `https://xhslink.com/Kri8yWim` | `Kri8yWim` | `Kri8yWim` | ✓ |
| 75 | `https://xhslink.com/aBsLW9K3` | `aBsLW9K3` | `aBsLW9K3` | ✓ |
| 76 | `https://xhslink.com/VceGf8JM` | `VceGf8JM` | `VceGf8JM` | ✓ |
| 77 | `https://xhslink.com/wxGbodAC` | `wxGbodAC` | `wxGbodAC` | ✓ |
| 78 | `https://xhslink.com/60Y9Jg3y` | `60Y9Jg3y` | `60Y9Jg3y` | ✓ |
| 79 | `https://xhslink.com/eL9q2XkG` | `eL9q2XkG` | `eL9q2XkG` | ✓ |
| 80 | `https://xhslink.com/yuKK0RZM` | `yuKK0RZM` | `yuKK0RZM` | ✓ |
| 81 | `https://xhslink.com/IcoJhpTa` | `IcoJhpTa` | `IcoJhpTa` | ✓ |
| 82 | `https://xhslink.com/XXYrhomX` | `XXYrhomX` | `XXYrhomX` | ✓ |
| 83 | `https://xhslink.com/7UZ749oW` | `7UZ749oW` | `7UZ749oW` | ✓ |
| 84 | `https://xhslink.com/paZprJ80` | `paZprJ80` | `paZprJ80` | ✓ |
| 85 | `https://xhslink.com/o9agxgo7` | `o9agxgo7` | `o9agxgo7` | ✓ |
| 86 | `https://xhslink.com/m9DFy9ZX` | `m9DFy9ZX` | `m9DFy9ZX` | ✓ |
| 87 | `https://xhslink.com/EnBnhU1P` | `EnBnhU1P` | `EnBnhU1P` | ✓ |
| 88 | `https://xhslink.com/W0HvgbhA` | `W0HvgbhA` | `W0HvgbhA` | ✓ |
| 89 | `https://xhslink.com/utQXZe5F` | `utQXZe5F` | `utQXZe5F` | ✓ |
| 90 | `https://xhslink.com/ErhAYTk9` | `ErhAYTk9` | `ErhAYTk9` | ✓ |
| 91 | `https://xhslink.com/WLBQYhJE` | `WLBQYhJE` | `WLBQYhJE` | ✓ |
| 92 | `https://xhslink.com/R9kemvJK` | `R9kemvJK` | `R9kemvJK` | ✓ |
| 93 | `https://xhslink.com/zCwWQ0qU` | `zCwWQ0qU` | `zCwWQ0qU` | ✓ |
| 94 | `https://xhslink.com/roqtF0JS` | `roqtF0JS` | `roqtF0JS` | ✓ |
| 95 | `https://xhslink.com/3RsKMyIi` | `3RsKMyIi` | `3RsKMyIi` | ✓ |
| 96 | `https://xhslink.com/qwkjTsKF` | `qwkjTsKF` | `qwkjTsKF` | ✓ |
| 97 | `https://xhslink.com/Ba035t83` | `Ba035t83` | `Ba035t83` | ✓ |
| 98 | `https://xhslink.com/SJuGUF0O` | `SJuGUF0O` | `SJuGUF0O` | ✓ |
| 99 | `https://xhslink.com/vK5NiFcC` | `vK5NiFcC` | `vK5NiFcC` | ✓ |
| 100 | `https://xhslink.com/0GlfBypy` | `0GlfBypy` | `0GlfBypy` | ✓ |
| 101 | `https://xhslink.com/t5vmHGIR` | `t5vmHGIR` | `t5vmHGIR` | ✓ |
| 102 | `https://xhslink.com/62HVX1Y3` | `62HVX1Y3` | `62HVX1Y3` | ✓ |
| 103 | `https://xhslink.com/HC8E05dm` | `HC8E05dm` | `HC8E05dm` | ✓ |
| 104 | `https://xhslink.com/RwNFG0jb` | `RwNFG0jb` | `RwNFG0jb` | ✓ |
| 105 | `https://xhslink.com/4KwcnjUF` | `4KwcnjUF` | `4KwcnjUF` | ✓ |
| 106 | `https://xhslink.com/lqNJqnrt` | `lqNJqnrt` | `lqNJqnrt` | ✓ |
| 107 | `https://xhslink.com/Qp33TLFk` | `Qp33TLFk` | `Qp33TLFk` | ✓ |
| 108 | `https://xhslink.com/fOYJTnkE` | `fOYJTnkE` | `fOYJTnkE` | ✓ |
| 109 | `https://xhslink.com/gFIhDOLx` | `gFIhDOLx` | `gFIhDOLx` | ✓ |
| 110 | `https://xhslink.com/paBmO0kU` | `paBmO0kU` | `paBmO0kU` | ✓ |
| 111 | `https://xhslink.com/RIC7NBvy` | `RIC7NBvy` | `RIC7NBvy` | ✓ |
| 112 | `https://xhslink.com/emx1PjRX` | `emx1PjRX` | `emx1PjRX` | ✓ |
| 113 | `https://xhslink.com/Qv8e3Iwx` | `Qv8e3Iwx` | `Qv8e3Iwx` | ✓ |
| 114 | `https://xhslink.com/m3fexgWY` | `m3fexgWY` | `m3fexgWY` | ✓ |
| 115 | `https://xhslink.com/5C7GkCRx` | `5C7GkCRx` | `5C7GkCRx` | ✓ |
| 116 | `https://xhslink.com/pVPM3PTS` | `pVPM3PTS` | `pVPM3PTS` | ✓ |
| 117 | `https://xhslink.com/94zaKKxL` | `94zaKKxL` | `94zaKKxL` | ✓ |
| 118 | `https://xhslink.com/siu7ZPxL` | `siu7ZPxL` | `siu7ZPxL` | ✓ |
| 119 | `https://xhslink.com/nhnkXP1n` | `nhnkXP1n` | `nhnkXP1n` | ✓ |
| 120 | `https://xhslink.com/N1vAM5x2` | `N1vAM5x2` | `N1vAM5x2` | ✓ |
| 121 | `https://xhslink.com/C1ci53PP` | `C1ci53PP` | `C1ci53PP` | ✓ |
| 122 | `https://xhslink.com/2M5P9RIY` | `2M5P9RIY` | `2M5P9RIY` | ✓ |
| 123 | `https://xhslink.com/8Q2DtZZZ` | `8Q2DtZZZ` | `8Q2DtZZZ` | ✓ |
| 124 | `https://xhslink.com/J3InH7iP` | `J3InH7iP` | `J3InH7iP` | ✓ |
| 125 | `https://xhslink.com/e3lCqSwL` | `e3lCqSwL` | `e3lCqSwL` | ✓ |
| 126 | `https://xhslink.com/NAwJbFV0` | `NAwJbFV0` | `NAwJbFV0` | ✓ |
| 127 | `https://xhslink.com/9yrRlrYD` | `9yrRlrYD` | `9yrRlrYD` | ✓ |
| 128 | `https://xhslink.com/SXMhNUAs` | `SXMhNUAs` | `SXMhNUAs` | ✓ |
| 129 | `https://xhslink.com/TJfYO8EU` | `TJfYO8EU` | `TJfYO8EU` | ✓ |
| 130 | `https://xhslink.com/D8LPCoIl` | `D8LPCoIl` | `D8LPCoIl` | ✓ |
| 131 | `https://xhslink.com/fYopPJfa` | `fYopPJfa` | `fYopPJfa` | ✓ |
| 132 | `https://xhslink.com/ugYt5Dru` | `ugYt5Dru` | `ugYt5Dru` | ✓ |
| 133 | `https://xhslink.com/uD74kLW9` | `uD74kLW9` | `uD74kLW9` | ✓ |
| 134 | `https://xhslink.com/ZkjhKjYB` | `ZkjhKjYB` | `ZkjhKjYB` | ✓ |
| 135 | `https://xhslink.com/daZnMsGd` | `daZnMsGd` | `daZnMsGd` | ✓ |
| 136 | `https://xhslink.com/SMDf1aXo` | `SMDf1aXo` | `SMDf1aXo` | ✓ |
| 137 | `https://xhslink.com/eaILRhVW` | `eaILRhVW` | `eaILRhVW` | ✓ |
| 138 | `https://xhslink.com/kA0df8mD` | `kA0df8mD` | `kA0df8mD` | ✓ |
| 139 | `https://xhslink.com/PECA8k6M` | `PECA8k6M` | `PECA8k6M` | ✓ |
| 140 | `https://xhslink.com/PMl7PuhZ` | `PMl7PuhZ` | `PMl7PuhZ` | ✓ |
| 141 | `https://xhslink.com/8QFFbO1k` | `8QFFbO1k` | `8QFFbO1k` | ✓ |
| 142 | `https://xhslink.com/e3c2VgFp` | `e3c2VgFp` | `e3c2VgFp` | ✓ |
| 143 | `https://xhslink.com/8CK8bnrt` | `8CK8bnrt` | `8CK8bnrt` | ✓ |
| 144 | `https://xhslink.com/37Q0lU3x` | `37Q0lU3x` | `37Q0lU3x` | ✓ |
| 145 | `https://xhslink.com/x3D3Cylw` | `x3D3Cylw` | `x3D3Cylw` | ✓ |
| 146 | `https://xhslink.com/LzZZSeNd` | `LzZZSeNd` | `LzZZSeNd` | ✓ |
| 147 | `https://xhslink.com/ky1gaCPx` | `ky1gaCPx` | `ky1gaCPx` | ✓ |
| 148 | `https://xhslink.com/QveEX7jA` | `QveEX7jA` | `QveEX7jA` | ✓ |
| 149 | `https://xhslink.com/DC9xr9Gi` | `DC9xr9Gi` | `DC9xr9Gi` | ✓ |
| 150 | `https://xhslink.com/H0NJfBg2` | `H0NJfBg2` | `H0NJfBg2` | ✓ |

### xhslink_a 类型

> App 分享的短链接格式（/a/ 路径）
>
> 共 100 个测试案例

| # | URL | 期望ID | 实际ID | 结果 |
|---|-----|--------|--------|------|
| 1 | `http://xhslink.com/a/0xZ8jH13` | `0xZ8jH13` | `0xZ8jH13` | ✓ |
| 2 | `http://xhslink.com/a/DkdE9YMA` | `DkdE9YMA` | `DkdE9YMA` | ✓ |
| 3 | `http://xhslink.com/a/NXdwvYaQ` | `NXdwvYaQ` | `NXdwvYaQ` | ✓ |
| 4 | `http://xhslink.com/a/Y8Nb8Q6s` | `Y8Nb8Q6s` | `Y8Nb8Q6s` | ✓ |
| 5 | `http://xhslink.com/a/quWUhQil` | `quWUhQil` | `quWUhQil` | ✓ |
| 6 | `http://xhslink.com/a/EvnMGb0y` | `EvnMGb0y` | `EvnMGb0y` | ✓ |
| 7 | `http://xhslink.com/a/w0IvE7rE` | `w0IvE7rE` | `w0IvE7rE` | ✓ |
| 8 | `http://xhslink.com/a/IJIJFafH` | `IJIJFafH` | `IJIJFafH` | ✓ |
| 9 | `http://xhslink.com/a/KfRfs6I7` | `KfRfs6I7` | `KfRfs6I7` | ✓ |
| 10 | `http://xhslink.com/a/h0JKfbP2` | `h0JKfbP2` | `h0JKfbP2` | ✓ |
| 11 | `http://xhslink.com/a/PF1kU0j6` | `PF1kU0j6` | `PF1kU0j6` | ✓ |
| 12 | `http://xhslink.com/a/OxGBpH9u` | `OxGBpH9u` | `OxGBpH9u` | ✓ |
| 13 | `http://xhslink.com/a/EvngfOk4` | `EvngfOk4` | `EvngfOk4` | ✓ |
| 14 | `http://xhslink.com/a/rroYqXad` | `rroYqXad` | `rroYqXad` | ✓ |
| 15 | `http://xhslink.com/a/ZhpGqDXu` | `ZhpGqDXu` | `ZhpGqDXu` | ✓ |
| 16 | `http://xhslink.com/a/NsQJxgPy` | `NsQJxgPy` | `NsQJxgPy` | ✓ |
| 17 | `http://xhslink.com/a/UyQswyDh` | `UyQswyDh` | `UyQswyDh` | ✓ |
| 18 | `http://xhslink.com/a/guhGlpvH` | `guhGlpvH` | `guhGlpvH` | ✓ |
| 19 | `http://xhslink.com/a/9ZiDccBZ` | `9ZiDccBZ` | `9ZiDccBZ` | ✓ |
| 20 | `http://xhslink.com/a/5ATC2BXv` | `5ATC2BXv` | `5ATC2BXv` | ✓ |
| 21 | `http://xhslink.com/a/hjshChI8` | `hjshChI8` | `hjshChI8` | ✓ |
| 22 | `http://xhslink.com/a/nvmjJVFa` | `nvmjJVFa` | `nvmjJVFa` | ✓ |
| 23 | `http://xhslink.com/a/Th6IS4Lj` | `Th6IS4Lj` | `Th6IS4Lj` | ✓ |
| 24 | `http://xhslink.com/a/65xlQkGD` | `65xlQkGD` | `65xlQkGD` | ✓ |
| 25 | `http://xhslink.com/a/aaiCAv2W` | `aaiCAv2W` | `aaiCAv2W` | ✓ |
| 26 | `http://xhslink.com/a/hQlE6G2I` | `hQlE6G2I` | `hQlE6G2I` | ✓ |
| 27 | `http://xhslink.com/a/3nKdyqQl` | `3nKdyqQl` | `3nKdyqQl` | ✓ |
| 28 | `http://xhslink.com/a/KVokWahp` | `KVokWahp` | `KVokWahp` | ✓ |
| 29 | `http://xhslink.com/a/LMNNJPd6` | `LMNNJPd6` | `LMNNJPd6` | ✓ |
| 30 | `http://xhslink.com/a/cynHnrMY` | `cynHnrMY` | `cynHnrMY` | ✓ |
| 31 | `http://xhslink.com/a/MZXlgyAq` | `MZXlgyAq` | `MZXlgyAq` | ✓ |
| 32 | `http://xhslink.com/a/j2HjgJvV` | `j2HjgJvV` | `j2HjgJvV` | ✓ |
| 33 | `http://xhslink.com/a/eJkiJVOZ` | `eJkiJVOZ` | `eJkiJVOZ` | ✓ |
| 34 | `http://xhslink.com/a/xhXoe0DO` | `xhXoe0DO` | `xhXoe0DO` | ✓ |
| 35 | `http://xhslink.com/a/supxxvJT` | `supxxvJT` | `supxxvJT` | ✓ |
| 36 | `http://xhslink.com/a/kebzm4zB` | `kebzm4zB` | `kebzm4zB` | ✓ |
| 37 | `http://xhslink.com/a/OciFZIQt` | `OciFZIQt` | `OciFZIQt` | ✓ |
| 38 | `http://xhslink.com/a/I6ULGV1z` | `I6ULGV1z` | `I6ULGV1z` | ✓ |
| 39 | `http://xhslink.com/a/FfP9C8lQ` | `FfP9C8lQ` | `FfP9C8lQ` | ✓ |
| 40 | `http://xhslink.com/a/kjAFds5T` | `kjAFds5T` | `kjAFds5T` | ✓ |
| 41 | `http://xhslink.com/a/0Vdi1FMO` | `0Vdi1FMO` | `0Vdi1FMO` | ✓ |
| 42 | `http://xhslink.com/a/b3tK4QHi` | `b3tK4QHi` | `b3tK4QHi` | ✓ |
| 43 | `http://xhslink.com/a/93TkFzaM` | `93TkFzaM` | `93TkFzaM` | ✓ |
| 44 | `http://xhslink.com/a/4JEDyNWu` | `4JEDyNWu` | `4JEDyNWu` | ✓ |
| 45 | `http://xhslink.com/a/lVnkYqL8` | `lVnkYqL8` | `lVnkYqL8` | ✓ |
| 46 | `http://xhslink.com/a/JSO0Ks6h` | `JSO0Ks6h` | `JSO0Ks6h` | ✓ |
| 47 | `http://xhslink.com/a/Lf50l2EX` | `Lf50l2EX` | `Lf50l2EX` | ✓ |
| 48 | `http://xhslink.com/a/mVfDhcBX` | `mVfDhcBX` | `mVfDhcBX` | ✓ |
| 49 | `http://xhslink.com/a/OAJVGyBj` | `OAJVGyBj` | `OAJVGyBj` | ✓ |
| 50 | `http://xhslink.com/a/Rv5hn3Rw` | `Rv5hn3Rw` | `Rv5hn3Rw` | ✓ |
| 51 | `http://xhslink.com/a/grYmIFCN` | `grYmIFCN` | `grYmIFCN` | ✓ |
| 52 | `http://xhslink.com/a/W3hFjoGw` | `W3hFjoGw` | `W3hFjoGw` | ✓ |
| 53 | `http://xhslink.com/a/e1zMoN2c` | `e1zMoN2c` | `e1zMoN2c` | ✓ |
| 54 | `http://xhslink.com/a/SXgBBBOl` | `SXgBBBOl` | `SXgBBBOl` | ✓ |
| 55 | `http://xhslink.com/a/nS5Ziko5` | `nS5Ziko5` | `nS5Ziko5` | ✓ |
| 56 | `http://xhslink.com/a/GRpXMIGS` | `GRpXMIGS` | `GRpXMIGS` | ✓ |
| 57 | `http://xhslink.com/a/NXsvdSJo` | `NXsvdSJo` | `NXsvdSJo` | ✓ |
| 58 | `http://xhslink.com/a/Rl9vc2Q6` | `Rl9vc2Q6` | `Rl9vc2Q6` | ✓ |
| 59 | `http://xhslink.com/a/EHmkmBYH` | `EHmkmBYH` | `EHmkmBYH` | ✓ |
| 60 | `http://xhslink.com/a/Z68yE4wM` | `Z68yE4wM` | `Z68yE4wM` | ✓ |
| 61 | `http://xhslink.com/a/11Ttz5pJ` | `11Ttz5pJ` | `11Ttz5pJ` | ✓ |
| 62 | `http://xhslink.com/a/xDie5A1U` | `xDie5A1U` | `xDie5A1U` | ✓ |
| 63 | `http://xhslink.com/a/hgtRnI7D` | `hgtRnI7D` | `hgtRnI7D` | ✓ |
| 64 | `http://xhslink.com/a/k4tkOyCU` | `k4tkOyCU` | `k4tkOyCU` | ✓ |
| 65 | `http://xhslink.com/a/trMZgjsc` | `trMZgjsc` | `trMZgjsc` | ✓ |
| 66 | `http://xhslink.com/a/SPMb4dLP` | `SPMb4dLP` | `SPMb4dLP` | ✓ |
| 67 | `http://xhslink.com/a/osFF82uo` | `osFF82uo` | `osFF82uo` | ✓ |
| 68 | `http://xhslink.com/a/pNz35Sx3` | `pNz35Sx3` | `pNz35Sx3` | ✓ |
| 69 | `http://xhslink.com/a/PXOxSIAJ` | `PXOxSIAJ` | `PXOxSIAJ` | ✓ |
| 70 | `http://xhslink.com/a/6aEp1ljT` | `6aEp1ljT` | `6aEp1ljT` | ✓ |
| 71 | `http://xhslink.com/a/CyRLaYJ2` | `CyRLaYJ2` | `CyRLaYJ2` | ✓ |
| 72 | `http://xhslink.com/a/oMue94ez` | `oMue94ez` | `oMue94ez` | ✓ |
| 73 | `http://xhslink.com/a/hwBXJ0yM` | `hwBXJ0yM` | `hwBXJ0yM` | ✓ |
| 74 | `http://xhslink.com/a/yTBQ5gjn` | `yTBQ5gjn` | `yTBQ5gjn` | ✓ |
| 75 | `http://xhslink.com/a/Gn8qDn7p` | `Gn8qDn7p` | `Gn8qDn7p` | ✓ |
| 76 | `http://xhslink.com/a/lBN8r6vN` | `lBN8r6vN` | `lBN8r6vN` | ✓ |
| 77 | `http://xhslink.com/a/9NiinFcf` | `9NiinFcf` | `9NiinFcf` | ✓ |
| 78 | `http://xhslink.com/a/nMU9rgGe` | `nMU9rgGe` | `nMU9rgGe` | ✓ |
| 79 | `http://xhslink.com/a/2yLy5ZCw` | `2yLy5ZCw` | `2yLy5ZCw` | ✓ |
| 80 | `http://xhslink.com/a/sA6JJo6n` | `sA6JJo6n` | `sA6JJo6n` | ✓ |
| 81 | `http://xhslink.com/a/bW1K9jwI` | `bW1K9jwI` | `bW1K9jwI` | ✓ |
| 82 | `http://xhslink.com/a/0B2DjVGy` | `0B2DjVGy` | `0B2DjVGy` | ✓ |
| 83 | `http://xhslink.com/a/ZShVO9si` | `ZShVO9si` | `ZShVO9si` | ✓ |
| 84 | `http://xhslink.com/a/WlXY7pNJ` | `WlXY7pNJ` | `WlXY7pNJ` | ✓ |
| 85 | `http://xhslink.com/a/iMZMfFia` | `iMZMfFia` | `iMZMfFia` | ✓ |
| 86 | `http://xhslink.com/a/5BRbJPzK` | `5BRbJPzK` | `5BRbJPzK` | ✓ |
| 87 | `http://xhslink.com/a/qT1gofNo` | `qT1gofNo` | `qT1gofNo` | ✓ |
| 88 | `http://xhslink.com/a/XRLATwAC` | `XRLATwAC` | `XRLATwAC` | ✓ |
| 89 | `http://xhslink.com/a/lokYlZle` | `lokYlZle` | `lokYlZle` | ✓ |
| 90 | `http://xhslink.com/a/clkvQtCx` | `clkvQtCx` | `clkvQtCx` | ✓ |
| 91 | `http://xhslink.com/a/WR1l4z5q` | `WR1l4z5q` | `WR1l4z5q` | ✓ |
| 92 | `http://xhslink.com/a/6DVUDZlZ` | `6DVUDZlZ` | `6DVUDZlZ` | ✓ |
| 93 | `http://xhslink.com/a/dxlRhWeD` | `dxlRhWeD` | `dxlRhWeD` | ✓ |
| 94 | `http://xhslink.com/a/UuCSLe3d` | `UuCSLe3d` | `UuCSLe3d` | ✓ |
| 95 | `http://xhslink.com/a/ZRWOdmE9` | `ZRWOdmE9` | `ZRWOdmE9` | ✓ |
| 96 | `http://xhslink.com/a/dvHry6bN` | `dvHry6bN` | `dvHry6bN` | ✓ |
| 97 | `http://xhslink.com/a/G4mSTyOv` | `G4mSTyOv` | `G4mSTyOv` | ✓ |
| 98 | `http://xhslink.com/a/vT2xBhWV` | `vT2xBhWV` | `vT2xBhWV` | ✓ |
| 99 | `http://xhslink.com/a/eS2mz1xN` | `eS2mz1xN` | `eS2mz1xN` | ✓ |
| 100 | `http://xhslink.com/a/gelaD9EA` | `gelaD9EA` | `gelaD9EA` | ✓ |

### invalid_domain 类型

> 无效域名测试（负面测试）
>
> 共 30 个测试案例

| # | URL | 期望ID | 实际ID | 结果 |
|---|-----|--------|--------|------|
| 1 | `https://douyin.com/explore/1255bd375a21b8ad2158a271` | `None` | `None` | ✓ |
| 2 | `https://douyin.com/explore/5c1535406eb6f0967d00a2fe` | `None` | `None` | ✓ |
| 3 | `https://redbook.com/explore/ff18997aba57c0f77050fbfc` | `None` | `None` | ✓ |
| 4 | `https://google.com/explore/2ac473702d1e754a67bda29b` | `None` | `None` | ✓ |
| 5 | `https://google.com/explore/d20a1c8fb240a6effd2045cd` | `None` | `None` | ✓ |
| 6 | `https://example.com/explore/030f8303c1a8c577499deabe` | `None` | `None` | ✓ |
| 7 | `https://example.com/explore/32aa88c8690408d9679b5aae` | `None` | `None` | ✓ |
| 8 | `https://google.com/explore/b3028026694ac4afe49cdfb1` | `None` | `None` | ✓ |
| 9 | `https://google.com/explore/80befb2d180326e12fff6036` | `None` | `None` | ✓ |
| 10 | `https://weibo.com/explore/3209b6ea641278e610675956` | `None` | `None` | ✓ |
| 11 | `https://google.com/explore/b1674c286b84fbcced869caf` | `None` | `None` | ✓ |
| 12 | `https://xhs.cn/explore/080ecda4b2beb7004f6edd45` | `None` | `None` | ✓ |
| 13 | `https://weibo.com/explore/4c1cb3844f6212794b25dfcd` | `None` | `None` | ✓ |
| 14 | `https://weibo.com/explore/69b9ca14e939bcff37756a81` | `None` | `None` | ✓ |
| 15 | `https://xhs.cn/explore/e6cc0b2f3dc281170f3b53e9` | `None` | `None` | ✓ |
| 16 | `https://xhs.cn/explore/57012866f04dca2cf103a88a` | `None` | `None` | ✓ |
| 17 | `https://weibo.com/explore/4c7402dc87d775a0f1d345a7` | `None` | `None` | ✓ |
| 18 | `https://xhs.cn/explore/e5a64ba44aa3c9829e6a7e89` | `None` | `None` | ✓ |
| 19 | `https://douyin.com/explore/a3799bcbc2dc46780e08f9ef` | `None` | `None` | ✓ |
| 20 | `https://redbook.com/explore/eff7b4b6fb8b39a0a3a77714` | `None` | `None` | ✓ |
| 21 | `https://xhs.cn/explore/dd449f405312fa39a11e1b95` | `None` | `None` | ✓ |
| 22 | `https://google.com/explore/b3dac689c2991a80e9142c01` | `None` | `None` | ✓ |
| 23 | `https://xhs.cn/explore/f3bb69c53e4642b9bdc70d75` | `None` | `None` | ✓ |
| 24 | `https://example.com/explore/3fba803005f618ebd0ed0962` | `None` | `None` | ✓ |
| 25 | `https://google.com/explore/a71b9e89f47286b479ad9c0d` | `None` | `None` | ✓ |
| 26 | `https://example.com/explore/4a30c5a86dc5121e56e62907` | `None` | `None` | ✓ |
| 27 | `https://xhs.cn/explore/c37c3ccfb72934d05bab179b` | `None` | `None` | ✓ |
| 28 | `https://weibo.com/explore/6343ca08815d423ff63ce2a2` | `None` | `None` | ✓ |
| 29 | `https://weibo.com/explore/335cb142849ecfeace6fdc4e` | `None` | `None` | ✓ |
| 30 | `https://douyin.com/explore/5681419a60033a433d4ade68` | `None` | `None` | ✓ |

### invalid_format 类型

> 无效格式测试（负面测试）
>
> 共 30 个测试案例

| # | URL | 期望ID | 实际ID | 结果 |
|---|-----|--------|--------|------|
| 1 | `https://www.xiaohongshu.com/search?keyword=test` | `None` | `None` | ✓ |
| 2 | `https://www.xiaohongshu.com/board/123` | `None` | `None` | ✓ |
| 3 | `not_a_url_at_all` | `None` | `None` | ✓ |
| 4 | `https://www.xiaohongshu.com/board/123` | `None` | `None` | ✓ |
| 5 | `https://www.xiaohongshu.com/search?keyword=test` | `None` | `None` | ✓ |
| 6 | `https://www.xiaohongshu.com/user/profile/123` | `None` | `None` | ✓ |
| 7 | `not_a_url_at_all` | `None` | `None` | ✓ |
| 8 | `not_a_url_at_all` | `None` | `None` | ✓ |
| 9 | `https://www.xiaohongshu.com/board/123` | `None` | `None` | ✓ |
| 10 | `https://www.xiaohongshu.com/` | `None` | `None` | ✓ |
| 11 | `https://www.xiaohongshu.com/user/profile/123` | `None` | `None` | ✓ |
| 12 | `https://www.xiaohongshu.com/search?keyword=test` | `None` | `None` | ✓ |
| 13 | `https://www.xiaohongshu.com/board/123` | `None` | `None` | ✓ |
| 14 | `https://www.xiaohongshu.com/user/profile/123` | `None` | `None` | ✓ |
| 15 | `https://www.xiaohongshu.com/user/profile/123` | `None` | `None` | ✓ |
| 16 | `https://www.xiaohongshu.com/board/123` | `None` | `None` | ✓ |
| 17 | `https://www.xiaohongshu.com/` | `None` | `None` | ✓ |
| 18 | `https://www.xiaohongshu.com/search?keyword=test` | `None` | `None` | ✓ |
| 19 | `https://www.xiaohongshu.com/search?keyword=test` | `None` | `None` | ✓ |
| 20 | `https://www.xiaohongshu.com/` | `None` | `None` | ✓ |
| 21 | `https://www.xiaohongshu.com/` | `None` | `None` | ✓ |
| 22 | `not_a_url_at_all` | `None` | `None` | ✓ |
| 23 | `https://www.xiaohongshu.com/search?keyword=test` | `None` | `None` | ✓ |
| 24 | `not_a_url_at_all` | `None` | `None` | ✓ |
| 25 | `https://www.xiaohongshu.com/user/profile/123` | `None` | `None` | ✓ |
| 26 | `not_a_url_at_all` | `None` | `None` | ✓ |
| 27 | `javascript:alert(1)` | `None` | `None` | ✓ |
| 28 | `https://www.xiaohongshu.com/user/profile/123` | `None` | `None` | ✓ |
| 29 | `https://www.xiaohongshu.com/user/profile/123` | `None` | `None` | ✓ |
| 30 | `https://www.xiaohongshu.com/board/123` | `None` | `None` | ✓ |

### empty 类型

> 空值/null 测试（边界测试）
>
> 共 20 个测试案例

| # | URL | 期望ID | 实际ID | 结果 |
|---|-----|--------|--------|------|
| 1 | `   ` | `None` | `None` | ✓ |
| 2 | `(空)` | `None` | `None` | ✓ |
| 3 | `(空)` | `None` | `None` | ✓ |
| 4 | `
	` | `None` | `None` | ✓ |
| 5 | `(空)` | `None` | `None` | ✓ |
| 6 | `(空)` | `None` | `None` | ✓ |
| 7 | `(空)` | `None` | `None` | ✓ |
| 8 | `   ` | `None` | `None` | ✓ |
| 9 | `
	` | `None` | `None` | ✓ |
| 10 | `(空)` | `None` | `None` | ✓ |
| 11 | `
	` | `None` | `None` | ✓ |
| 12 | `
	` | `None` | `None` | ✓ |
| 13 | `(空)` | `None` | `None` | ✓ |
| 14 | `
	` | `None` | `None` | ✓ |
| 15 | `(空)` | `None` | `None` | ✓ |
| 16 | `(空)` | `None` | `None` | ✓ |
| 17 | `
	` | `None` | `None` | ✓ |
| 18 | `(空)` | `None` | `None` | ✓ |
| 19 | `
	` | `None` | `None` | ✓ |
| 20 | `
	` | `None` | `None` | ✓ |

### malformed 类型

> 畸形 URL 测试（边界测试）
>
> 共 20 个测试案例

| # | URL | 期望ID | 实际ID | 结果 |
|---|-----|--------|--------|------|
| 1 | `https://www.xiaohongshu.com/explore/` | `None` | `None` | ✓ |
| 2 | `xiaohongshu.com/explore/abc123` | `abc123` | `abc123` | ✓ |
| 3 | `xiaohongshu.com/explore/abc123` | `abc123` | `abc123` | ✓ |
| 4 | `//www.xiaohongshu.com/explore/abc123` | `abc123` | `abc123` | ✓ |
| 5 | `//www.xiaohongshu.com/explore/abc123` | `abc123` | `abc123` | ✓ |
| 6 | `//www.xiaohongshu.com/explore/abc123` | `abc123` | `abc123` | ✓ |
| 7 | `xiaohongshu.com/explore/abc123` | `abc123` | `abc123` | ✓ |
| 8 | `https://www.xiaohongshu.com/explore/abc123/extra/path` | `abc123` | `abc123` | ✓ |
| 9 | `//www.xiaohongshu.com/explore/abc123` | `abc123` | `abc123` | ✓ |
| 10 | `https://www.xiaohongshu.com/explore` | `None` | `None` | ✓ |
| 11 | `xiaohongshu.com/explore/abc123` | `abc123` | `abc123` | ✓ |
| 12 | `https://www.xiaohongshu.com/explore/` | `None` | `None` | ✓ |
| 13 | `xiaohongshu.com/explore/abc123` | `abc123` | `abc123` | ✓ |
| 14 | `https://www.xiaohongshu.com/explore/` | `None` | `None` | ✓ |
| 15 | `https://www.xiaohongshu.com/explore/abc123/extra/path` | `abc123` | `abc123` | ✓ |
| 16 | `https://www.xiaohongshu.com/explore/` | `None` | `None` | ✓ |
| 17 | `//www.xiaohongshu.com/explore/abc123` | `abc123` | `abc123` | ✓ |
| 18 | `https://www.xiaohongshu.com/explore/` | `None` | `None` | ✓ |
| 19 | `xiaohongshu.com/explore/abc123` | `abc123` | `abc123` | ✓ |
| 20 | `https://www.xiaohongshu.com/explore/` | `None` | `None` | ✓ |

## 附录

### 支持的 URL 模式

```python
PATTERNS = [
    r"xiaohongshu\.com/explore/([a-zA-Z0-9]+)",
    r"xiaohongshu\.com/discovery/item/([a-zA-Z0-9]+)",
    r"xhslink\.com/a/([a-zA-Z0-9]+)",
    r"xhslink\.com/([a-zA-Z0-9]+)",
]
```

### 测试环境

- Python 3.11+
- 测试框架: 自定义测试脚本
- 生成时间: 2026-01-05 21:56:06
