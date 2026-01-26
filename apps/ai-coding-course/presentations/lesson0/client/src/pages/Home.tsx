import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { AnimatePresence, motion } from "framer-motion";
import { ArrowRight, CheckCircle2, Code2, Globe, Laptop, Terminal, Zap } from "lucide-react";
import { useState } from "react";

// 课程内容数据
const lessonData = {
  title: "AI辅助产品开发实战",
  subtitle: "Lesson 0：课程导学与环境准备",
  intro: "面向零代码基础的产品人员，通过AI编程助手实现完整小程序产品。本课程将带你从零开始，构建 TeamVenture AI团建策划助手。",
  sections: [
    {
      id: "0.1",
      title: "课程介绍与学习方法",
      icon: <Zap className="w-5 h-5" />,
      content: (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="glass p-6 rounded-xl">
              <h3 className="text-xl font-bold font-['Orbitron'] mb-4 text-primary">学习方法循环</h3>
              <ul className="space-y-4">
                <li className="flex items-start gap-3">
                  <div className="bg-primary/20 p-2 rounded-lg text-primary"><Globe className="w-4 h-4" /></div>
                  <div>
                    <span className="font-bold text-white">1. 观察</span>
                    <p className="text-sm text-muted-foreground">看AI如何生成代码，理解输入与输出的关系。</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <div className="bg-primary/20 p-2 rounded-lg text-primary"><Code2 className="w-4 h-4" /></div>
                  <div>
                    <span className="font-bold text-white">2. 理解</span>
                    <p className="text-sm text-muted-foreground">理解代码背后的业务逻辑，而非死记语法。</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <div className="bg-primary/20 p-2 rounded-lg text-primary"><CheckCircle2 className="w-4 h-4" /></div>
                  <div>
                    <span className="font-bold text-white">3. 验证</span>
                    <p className="text-sm text-muted-foreground">在真实环境中运行，检查功能是否符合预期。</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <div className="bg-primary/20 p-2 rounded-lg text-primary"><ArrowRight className="w-4 h-4" /></div>
                  <div>
                    <span className="font-bold text-white">4. 迭代</span>
                    <p className="text-sm text-muted-foreground">根据结果调整需求描述，引导AI优化。</p>
                  </div>
                </li>
              </ul>
            </div>
            <div className="glass p-6 rounded-xl border-l-4 border-l-destructive">
              <h3 className="text-xl font-bold font-['Orbitron'] mb-4 text-destructive">你不需要做的</h3>
              <ul className="space-y-3">
                <li className="flex items-center gap-2 text-muted-foreground">
                  <span className="text-destructive">❌</span> 记住任何编程语法
                </li>
                <li className="flex items-center gap-2 text-muted-foreground">
                  <span className="text-destructive">❌</span> 理解底层技术原理
                </li>
                <li className="flex items-center gap-2 text-muted-foreground">
                  <span className="text-destructive">❌</span> 有任何编程经验
                </li>
              </ul>
              <div className="mt-6 pt-6 border-t border-white/10">
                <h3 className="text-xl font-bold font-['Orbitron'] mb-4 text-green-400">你需要做的</h3>
                <ul className="space-y-3">
                  <li className="flex items-center gap-2 text-white">
                    <span className="text-green-400">✅</span> 清晰描述产品需求
                  </li>
                  <li className="flex items-center gap-2 text-white">
                    <span className="text-green-400">✅</span> 验证功能是否符合预期
                  </li>
                  <li className="flex items-center gap-2 text-white">
                    <span className="text-green-400">✅</span> 学会与AI高效沟通
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      )
    },
    {
      id: "0.2",
      title: "VPN与网络环境",
      icon: <Globe className="w-5 h-5" />,
      content: (
        <div className="space-y-6">
          <p className="text-lg text-muted-foreground">Claude Code 等 AI 工具需要访问国际网络。推荐使用机场服务（个人学习）或企业VPN。</p>
          
          <div className="glass p-6 rounded-xl">
            <h3 className="text-xl font-bold font-['Orbitron'] mb-4 text-primary">配置要点</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-background/50 p-4 rounded-lg border border-white/5">
                <div className="text-4xl font-bold text-white/10 mb-2">01</div>
                <h4 className="font-bold text-white mb-2">全局代理</h4>
                <p className="text-sm text-muted-foreground">选择 Global 模式而非 PAC，确保命令行工具也能走代理。</p>
              </div>
              <div className="bg-background/50 p-4 rounded-lg border border-white/5">
                <div className="text-4xl font-bold text-white/10 mb-2">02</div>
                <h4 className="font-bold text-white mb-2">验证访问</h4>
                <p className="text-sm text-muted-foreground">尝试访问 <code className="text-primary">claude.ai</code>，确保能正常打开。</p>
              </div>
              <div className="bg-background/50 p-4 rounded-lg border border-white/5">
                <div className="text-4xl font-bold text-white/10 mb-2">03</div>
                <h4 className="font-bold text-white mb-2">节点选择</h4>
                <p className="text-sm text-muted-foreground">连接不稳定时，优先切换到日本或新加坡节点。</p>
              </div>
            </div>
          </div>
        </div>
      )
    },
    {
      id: "0.3",
      title: "Git 版本控制",
      icon: <Code2 className="w-5 h-5" />,
      content: (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <p className="text-lg text-muted-foreground">代码的"时光机"，让你随时回退到任意历史版本。</p>
            <div className="bg-black/30 px-4 py-2 rounded font-mono text-sm text-green-400 border border-green-400/30">
              $ git --version
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { title: "Repository", desc: "项目文件夹", detail: "存放所有代码的地方" },
              { title: "Commit", desc: "存档点", detail: "保存当前状态的快照" },
              { title: "Branch", desc: "平行世界", detail: "同时开发多个功能" },
              { title: "Pull/Push", desc: "上传/下载", detail: "与云端同步代码" }
            ].map((item, i) => (
              <div key={i} className="glass p-4 rounded-xl hover:bg-primary/10 transition-colors cursor-default group">
                <h4 className="font-bold text-white group-hover:text-primary transition-colors">{item.title}</h4>
                <div className="text-xs font-mono text-primary/70 mb-2">{item.desc}</div>
                <p className="text-sm text-muted-foreground">{item.detail}</p>
              </div>
            ))}
          </div>
        </div>
      )
    },
    {
      id: "0.4",
      title: "Claude Code 工具",
      icon: <Terminal className="w-5 h-5" />,
      content: (
        <div className="space-y-6">
          <div className="glass p-8 rounded-xl border-primary/30 relative overflow-hidden">
            <div className="absolute top-0 right-0 p-4 opacity-10">
              <Terminal className="w-32 h-32" />
            </div>
            <h3 className="text-2xl font-bold font-['Orbitron'] mb-2 text-white">Claude Code</h3>
            <p className="text-primary mb-6">Anthropic 开发的终端 AI 编程助手</p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div>
                <h4 className="font-bold text-white mb-4 border-b border-white/10 pb-2">核心能力</h4>
                <ul className="space-y-2">
                  {["代码生成 - 根据需求写代码", "代码解释 - 解释看不懂的代码", "问题修复 - 自动分析并修复Bug", "代码重构 - 优化代码结构"].map((item, i) => (
                    <li key={i} className="flex items-center gap-2 text-sm text-muted-foreground">
                      <div className="w-1.5 h-1.5 rounded-full bg-primary"></div>
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <h4 className="font-bold text-white mb-4 border-b border-white/10 pb-2">安装命令</h4>
                <div className="bg-black/50 p-4 rounded-lg font-mono text-sm text-gray-300 border border-white/10">
                  <span className="text-gray-500"># 需要 Node.js 环境</span><br/>
                  npm install -g @anthropic-ai/claude-code
                </div>
                <div className="mt-4 flex items-center gap-2 text-xs text-green-400">
                  <CheckCircle2 className="w-3 h-3" />
                  验证: claude --version
                </div>
              </div>
            </div>
          </div>
        </div>
      )
    },
    {
      id: "0.5",
      title: "微信小程序基础",
      icon: <Laptop className="w-5 h-5" />,
      content: (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="glass p-6 rounded-xl">
              <h3 className="text-lg font-bold font-['Orbitron'] mb-4 text-white">文件结构</h3>
              <div className="space-y-3 font-mono text-sm">
                <div className="flex items-center gap-3 p-2 rounded hover:bg-white/5 transition-colors">
                  <span className="text-blue-400 font-bold">.wxml</span>
                  <span className="text-muted-foreground">结构 (HTML)</span>
                </div>
                <div className="flex items-center gap-3 p-2 rounded hover:bg-white/5 transition-colors">
                  <span className="text-pink-400 font-bold">.wxss</span>
                  <span className="text-muted-foreground">样式 (CSS)</span>
                </div>
                <div className="flex items-center gap-3 p-2 rounded hover:bg-white/5 transition-colors">
                  <span className="text-yellow-400 font-bold">.js</span>
                  <span className="text-muted-foreground">逻辑 (JavaScript)</span>
                </div>
                <div className="flex items-center gap-3 p-2 rounded hover:bg-white/5 transition-colors">
                  <span className="text-gray-400 font-bold">.json</span>
                  <span className="text-muted-foreground">配置</span>
                </div>
              </div>
            </div>
            
            <div className="glass p-6 rounded-xl">
              <h3 className="text-lg font-bold font-['Orbitron'] mb-4 text-white">本地存储 API</h3>
              <div className="space-y-4">
                <div className="bg-black/30 p-3 rounded border border-white/5">
                  <div className="text-xs text-gray-500 mb-1">// 保存数据</div>
                  <code className="text-sm text-green-300">wx.setStorageSync('key', value)</code>
                </div>
                <div className="bg-black/30 p-3 rounded border border-white/5">
                  <div className="text-xs text-gray-500 mb-1">// 读取数据</div>
                  <code className="text-sm text-blue-300">const data = wx.getStorageSync('key')</code>
                </div>
              </div>
            </div>
          </div>
        </div>
      )
    },
    {
      id: "0.6",
      title: "案例项目：TeamVenture",
      icon: <Globe className="w-5 h-5" />,
      content: (
        <div className="space-y-6">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold font-['Orbitron'] text-transparent bg-clip-text bg-gradient-to-r from-primary to-purple-400 mb-2">TeamVenture</h2>
            <p className="text-muted-foreground">AI 团建策划助手</p>
          </div>

          <div className="relative">
            <div className="absolute left-1/2 -translate-x-1/2 top-0 bottom-0 w-0.5 bg-gradient-to-b from-primary/50 to-transparent hidden md:block"></div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 relative">
              {[
                { step: "01", title: "需求收集", desc: "输入人数、预算、偏好" },
                { step: "02", title: "方案生成", desc: "AI 智能生成 3 套方案" },
                { step: "03", title: "方案管理", desc: "保存、对比、确认方案" },
                { step: "04", title: "供应商对接", desc: "一键联系合作供应商" }
              ].map((item, i) => (
                <div key={i} className={`flex items-center gap-4 ${i % 2 === 0 ? 'md:flex-row-reverse md:text-right' : ''}`}>
                  <div className="glass p-4 rounded-xl flex-1 hover:border-primary/50 transition-colors">
                    <div className="text-xs font-mono text-primary mb-1">STEP {item.step}</div>
                    <h4 className="font-bold text-white mb-1">{item.title}</h4>
                    <p className="text-sm text-muted-foreground">{item.desc}</p>
                  </div>
                  <div className="w-3 h-3 rounded-full bg-primary shadow-[0_0_10px_var(--primary)] hidden md:block z-10"></div>
                  <div className="flex-1 hidden md:block"></div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )
    }
  ]
};

export default function Home() {
  const [activeTab, setActiveTab] = useState("0.1");

  return (
    <div className="min-h-screen bg-background text-foreground font-['Rajdhani'] selection:bg-primary selection:text-white pb-20">
      {/* Hero Section */}
      <header className="relative pt-20 pb-16 px-6 overflow-hidden">
        <div className="absolute top-0 left-0 w-full h-full bg-[url('https://images.unsplash.com/photo-1550751827-4bd374c3f58b?q=80&w=2070&auto=format&fit=crop')] bg-cover bg-center opacity-10 pointer-events-none"></div>
        <div className="absolute inset-0 bg-gradient-to-b from-background via-transparent to-background pointer-events-none"></div>
        
        <div className="container relative z-10 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <div className="inline-block px-3 py-1 mb-4 border border-primary/30 rounded-full bg-primary/10 text-primary text-sm font-mono tracking-wider">
              LESSON 0
            </div>
            <h1 className="text-5xl md:text-7xl font-black font-['Orbitron'] mb-6 tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-white via-gray-200 to-gray-500 drop-shadow-[0_0_15px_rgba(255,255,255,0.1)]">
              {lessonData.title}
            </h1>
            <p className="text-xl md:text-2xl text-muted-foreground max-w-2xl mx-auto font-light leading-relaxed">
              {lessonData.subtitle}
            </p>
          </motion.div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container px-4 md:px-6">
        <Tabs defaultValue="0.1" value={activeTab} onValueChange={setActiveTab} className="w-full max-w-5xl mx-auto">
          <div className="flex flex-col md:flex-row gap-8">
            {/* Sidebar Navigation */}
            <div className="w-full md:w-64 flex-shrink-0">
              <div className="sticky top-8">
                <TabsList className="flex flex-col h-auto w-full bg-transparent gap-2 p-0">
                  {lessonData.sections.map((section) => (
                    <TabsTrigger
                      key={section.id}
                      value={section.id}
                      className="w-full justify-start px-4 py-3 h-auto text-left data-[state=active]:bg-primary/20 data-[state=active]:text-primary data-[state=active]:border-l-2 data-[state=active]:border-primary rounded-r-lg rounded-l-none border-l-2 border-transparent transition-all hover:bg-white/5"
                    >
                      <div className="flex items-center gap-3">
                        <span className="text-xs font-mono opacity-50">{section.id}</span>
                        <span className="font-medium truncate">{section.title}</span>
                      </div>
                    </TabsTrigger>
                  ))}
                </TabsList>
                
                <div className="mt-8 p-4 glass rounded-xl border border-primary/20">
                  <h4 className="text-sm font-bold text-white mb-2 flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-green-400" />
                    课后作业
                  </h4>
                  <p className="text-xs text-muted-foreground mb-3">完成环境配置清单与思考题。</p>
                  <Button size="sm" className="w-full bg-primary hover:bg-primary/80 text-white" onClick={() => window.open('https://claude.ai', '_blank')}>
                    访问 Claude.ai
                  </Button>
                </div>
              </div>
            </div>

            {/* Content Area */}
            <div className="flex-1 min-w-0">
              <AnimatePresence mode="wait">
                <motion.div
                  key={activeTab}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  {lessonData.sections.map((section) => (
                    <TabsContent key={section.id} value={section.id} className="mt-0 focus-visible:outline-none">
                      <Card className="glass border-none overflow-hidden">
                        <CardHeader className="border-b border-white/5 pb-6">
                          <div className="flex items-center gap-3 mb-2">
                            <div className="p-2 bg-primary/10 rounded-lg text-primary">
                              {section.icon}
                            </div>
                            <span className="font-mono text-sm text-primary/70">UNIT {section.id}</span>
                          </div>
                          <CardTitle className="text-3xl font-['Orbitron']">{section.title}</CardTitle>
                        </CardHeader>
                        <CardContent className="pt-8">
                          {section.content}
                        </CardContent>
                      </Card>
                    </TabsContent>
                  ))}
                </motion.div>
              </AnimatePresence>
              
              <div className="flex justify-between mt-8">
                <Button
                  variant="outline"
                  onClick={() => {
                    const currentIndex = lessonData.sections.findIndex(s => s.id === activeTab);
                    if (currentIndex > 0) setActiveTab(lessonData.sections[currentIndex - 1].id);
                  }}
                  disabled={activeTab === lessonData.sections[0].id}
                  className="border-white/10 hover:bg-white/5"
                >
                  上一单元
                </Button>
                <Button
                  onClick={() => {
                    const currentIndex = lessonData.sections.findIndex(s => s.id === activeTab);
                    if (currentIndex < lessonData.sections.length - 1) setActiveTab(lessonData.sections[currentIndex + 1].id);
                  }}
                  disabled={activeTab === lessonData.sections[lessonData.sections.length - 1].id}
                  className="bg-primary hover:bg-primary/80 text-white"
                >
                  下一单元
                </Button>
              </div>
            </div>
          </div>
        </Tabs>
      </main>
    </div>
  );
}
