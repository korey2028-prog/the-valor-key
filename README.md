# The Valor Key 🔑

A 5/21 memorial website for Valentina.

> "Not just on February 14th... Happy Valentina's Day · May 21, 2026"

## Stack

- **Framework**: Astro 4 + Tailwind CSS
- **Deployment**: GitHub Pages
- **Architecture**: Static SPA, no backend, all content in `src/data/data.json`

## Local Development

```bash
npm install
npm run dev
```

Open http://localhost:4321

## Build

```bash
npm run build
```

Output: `dist/`

## Deploy to GitHub Pages

1. Create a GitHub repo named `the-valor-key`
2. Push this code to `main` branch
3. In repo Settings → Pages → Source: **GitHub Actions**
4. The workflow at `.github/workflows/deploy.yml` will auto-deploy
5. Site will be live at: `https://korey2028-prog.github.io/the-valor-key/`

## Project Structure

```
the-valor-key/
├─ src/
│  ├─ components/
│  │  ├─ Hero.astro          # 首屏: VALENTINE → VAL+OR+KEY 动画
│  │  ├─ WorldMap.astro      # 跨国漫游图: SVG 地图 + 小飞机
│  │  ├─ KeyHover.astro      # 钥匙点击彩蛋: "Gondolok rád, mindig"
│  │  └─ AudioControl.astro  # 背景音乐控制
│  ├─ layouts/
│  │  └─ Layout.astro
│  ├─ pages/
│  │  └─ index.astro         # 主页
│  ├─ data/
│  │  └─ data.json           # 所有内容
│  └─ styles/
│     └─ global.css
└─ public/
   ├─ audio/                 # 背景音乐 mp3
   └─ favicon.svg
```

## Customization

所有文案、城市、飞行路径都在 `src/data/data.json` 里。后续添加新模块只改数据 + 加组件。
