# Pandora-Vercel
本项目修改了 `Pandora-Cloud` 的代码结构，使其能够在 `vercel` 以及 `Zeabur` 上部署  

## 一键部署
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fchrysoljq%2Fpandora-vercel&project-name=pandora-vercel&framework=other)
+ 测试网站 [https://pandora-vercel-lovat.vercel.app/](https://pandora-vercel-lovat.vercel.app/)
+ 本地运行
```bash
npm install -g vercel
vercel dev
```
## Todo
- [ ] vercel 路由问题
  目前删除了文件夹中包含的 `[`, `]` 字符，暂未知有何影响