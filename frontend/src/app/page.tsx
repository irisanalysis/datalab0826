import { Metadata } from 'next';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  BarChart3, 
  Brain, 
  Database, 
  FileSpreadsheet, 
  MessageSquare, 
  PieChart, 
  Zap,
  TrendingUp,
  Users,
  Shield
} from 'lucide-react';

export const metadata: Metadata = {
  title: 'AI数据分析平台 | 智能数据洞察',
  description: '使用先进AI技术，将复杂数据转化为有价值的业务洞察。支持自然语言查询、自动化分析和交互式可视化。',
};

const features = [
  {
    icon: Brain,
    title: 'AI智能分析',
    description: '使用自然语言描述你的问题，AI会自动理解并执行相应的数据分析',
    color: 'text-blue-500',
    bgColor: 'bg-blue-50 dark:bg-blue-950',
  },
  {
    icon: MessageSquare,
    title: '对话式查询',
    description: '通过对话方式探索数据，获得即时的分析结果和可视化图表',
    color: 'text-green-500',
    bgColor: 'bg-green-50 dark:bg-green-950',
  },
  {
    icon: BarChart3,
    title: '智能可视化',
    description: '自动推荐最适合的图表类型，生成专业级的数据可视化报告',
    color: 'text-purple-500',
    bgColor: 'bg-purple-50 dark:bg-purple-950',
  },
  {
    icon: Database,
    title: '多源数据集成',
    description: '支持CSV、Excel、JSON等多种格式，轻松上传和管理你的数据集',
    color: 'text-orange-500',
    bgColor: 'bg-orange-50 dark:bg-orange-950',
  },
  {
    icon: Zap,
    title: '实时分析',
    description: '基于Ray集群的分布式计算，处理大规模数据集的实时分析需求',
    color: 'text-yellow-500',
    bgColor: 'bg-yellow-50 dark:bg-yellow-950',
  },
  {
    icon: PieChart,
    title: '高级统计',
    description: '提供回归分析、聚类分析、相关性分析等专业统计分析功能',
    color: 'text-red-500',
    bgColor: 'bg-red-50 dark:bg-red-950',
  },
];

const stats = [
  { label: '数据集处理', value: '10M+', icon: FileSpreadsheet },
  { label: '分析任务完成', value: '500K+', icon: TrendingUp },
  { label: '企业用户', value: '1000+', icon: Users },
  { label: '数据安全保障', value: '99.9%', icon: Shield },
];

export default function HomePage() {
  return (
    <div className="flex flex-col">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 py-20 px-4">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center">
            <Badge variant="secondary" className="mb-4">
              🚀 基于GPT-4和Ray集群的企业级平台
            </Badge>
            <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-6">
              <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                AI数据分析平台
              </span>
            </h1>
            <p className="text-xl md:text-2xl text-muted-foreground mb-8 max-w-3xl mx-auto">
              让每个人都能成为数据科学家。通过自然语言对话，瞬间获得专业的数据洞察和可视化报告。
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Button size="lg" className="text-lg px-8" asChild>
                <Link href="/dashboard">
                  开始分析
                </Link>
              </Button>
              <Button size="lg" variant="outline" className="text-lg px-8" asChild>
                <Link href="/datasets">
                  上传数据
                </Link>
              </Button>
            </div>
          </div>
        </div>
        
        {/* Animated background elements */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute -top-40 -right-40 w-80 h-80 rounded-full bg-blue-200 opacity-20 animate-pulse-slow"></div>
          <div className="absolute -bottom-40 -left-40 w-80 h-80 rounded-full bg-purple-200 opacity-20 animate-pulse-slow delay-1000"></div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">强大的功能特性</h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              集成最新AI技术和分布式计算能力，为您提供企业级数据分析解决方案
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <Card key={index} className="group hover:shadow-lg transition-all duration-300 border-0 bg-gradient-to-br from-white to-gray-50 dark:from-slate-800 dark:to-slate-900">
                <CardHeader>
                  <div className={`w-12 h-12 rounded-lg ${feature.bgColor} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300`}>
                    <feature.icon className={`w-6 h-6 ${feature.color}`} />
                  </div>
                  <CardTitle className="text-xl">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-base leading-relaxed">
                    {feature.description}
                  </CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20 px-4 bg-muted/30">
        <div className="container mx-auto max-w-4xl">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">值得信赖的数字</h2>
            <p className="text-xl text-muted-foreground">
              服务全球企业用户，处理海量数据，提供可靠的分析服务
            </p>
          </div>
          
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-4">
                  <stat.icon className="w-8 h-8 text-primary" />
                </div>
                <div className="text-3xl md:text-4xl font-bold text-primary mb-2">
                  {stat.value}
                </div>
                <div className="text-muted-foreground font-medium">
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4">
        <div className="container mx-auto max-w-4xl text-center">
          <Card className="bg-gradient-to-r from-blue-600 to-purple-600 border-0 text-white">
            <CardHeader className="pb-8 pt-12">
              <CardTitle className="text-3xl md:text-4xl font-bold mb-4">
                准备好开始你的数据分析之旅了吗？
              </CardTitle>
              <CardDescription className="text-xl text-blue-100 max-w-2xl mx-auto">
                无需编程经验，只需简单对话，即可获得专业的数据洞察。立即开始，探索数据的无限可能。
              </CardDescription>
            </CardHeader>
            <CardContent className="pb-12">
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Button size="lg" variant="secondary" className="text-lg px-8" asChild>
                  <Link href="/auth/register">
                    免费注册
                  </Link>
                </Button>
                <Button size="lg" variant="outline" className="text-lg px-8 bg-transparent border-white text-white hover:bg-white hover:text-blue-600" asChild>
                  <Link href="/ai-chat">
                    体验AI分析
                  </Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t py-12 px-4 bg-muted/20">
        <div className="container mx-auto max-w-6xl">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="col-span-1 md:col-span-2">
              <h3 className="text-2xl font-bold mb-4">AI数据分析平台</h3>
              <p className="text-muted-foreground mb-4 max-w-md">
                让数据分析变得简单、智能、高效。基于最新AI技术，为企业提供专业的数据洞察服务。
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">产品功能</h4>
              <ul className="space-y-2 text-muted-foreground">
                <li><Link href="/datasets" className="hover:text-primary">数据管理</Link></li>
                <li><Link href="/analysis" className="hover:text-primary">智能分析</Link></li>
                <li><Link href="/visualizations" className="hover:text-primary">数据可视化</Link></li>
                <li><Link href="/ai-chat" className="hover:text-primary">AI对话</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">支持</h4>
              <ul className="space-y-2 text-muted-foreground">
                <li><Link href="/docs" className="hover:text-primary">使用文档</Link></li>
                <li><Link href="/support" className="hover:text-primary">技术支持</Link></li>
                <li><Link href="/privacy" className="hover:text-primary">隐私政策</Link></li>
                <li><Link href="/terms" className="hover:text-primary">服务条款</Link></li>
              </ul>
            </div>
          </div>
          <div className="border-t mt-12 pt-8 text-center text-muted-foreground">
            <p>&copy; 2024 AI数据分析平台. 保留所有权利.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}