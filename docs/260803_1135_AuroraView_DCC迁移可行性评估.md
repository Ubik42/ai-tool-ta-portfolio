# AuroraView DCC 迁移可行性评估

> 评估时间：2026-08-03 11:35  
> 参考仓：`<local-workspace>\_reference\github\_front_end\auroraview`  
> 当前上游：`692b779b chore(main): release auroraview 0.5.10` / `auroraview-v0.5.10`

## 一.结论

可行，而且应该作为作品集展示方向的主路径。

当前 portfolio 前端不应继续作为最终主展示入口。它更适合降级为证据台、索引页和 public case package 浏览器。核心展示应迁移到 DCC 内，优先 Maya：用 AuroraView 的 `QtWebView` 把 React UI 嵌入 Maya Qt 窗口，再通过 Python API bridge 调 Maya 场景、选择、attr、检查、导出等真实工具逻辑。

AuroraView 已经具备我们需要的关键能力：

- `QtWebView`：面向 Maya / Houdini / Nuke / 3ds Max 的 Qt widget 嵌入。
- `create_webview(parent=maya_main_window(), ...)`：根据 parent 自动选择 Qt 路径。
- `bind_api` / `bind_call` / `webview.on` / `webview.emit`：前端和 DCC Python 双向通信。
- `load_file` / `asset_root` / `auroraview://`：加载本地 React/Vite 静态资源。
- Maya 示例 `examples\maya_qt_echo_demo.py`：已证明能在 Maya Qt Dialog 里嵌 Web UI，并让 JS 调 Maya Python。

## 二.已执行更新

本地 `auroraview` 仓库已从 GitHub 更新到上游最新 `origin/main`。

由于本地 `main` 比上游多 2 个本地同步提交，上游领先 621 个提交，直接 `git pull --ff-only` 失败。已先备份原本地分支：

```text
ubik/main-before-upstream-sync-20260803-113326
```

随后当前 `main` 已切到：

```text
692b779b (HEAD -> main, tag: auroraview-v0.5.10, origin/main, origin/HEAD)
```

## 三.对当前作品集前端的迁移判断

当前前端工程：

```text
<repo>\showcases\portfolio-site
```

技术特征：

- Vite + React。
- 依赖很轻：`react` / `react-dom` / `lucide-react`。
- 没有远端接口依赖。
- `dist` 当前只有 1 个 JS、1 个 CSS、favicon，总体约 2.18 MB。

这说明它很适合被 AuroraView 加载。

评估时发现 `vite.config.ts` 没有设置 `base: './'`，所以旧版 `dist/index.html` 里生成的是：

```html
<script type="module" crossorigin src="/assets/index-5KhlOrL-.js"></script>
<link rel="stylesheet" crossorigin href="/assets/index-DEdEotZ9.css">
```

这在浏览器 dev server 下没问题，但在 DCC 本地加载里不稳。当前已将 Vite 配置修正为相对路径构建：

```ts
// vite.config.ts
export default defineConfig({
  base: "./",
  plugins: [react()],
});
```

当前 `dist/index.html` 已生成 `./assets/...` 相对资源路径，可用于 AuroraView `load_file` / `asset_root` 加载。

## 四.推荐迁移架构

```text
Maya Shelf Button
  -> Python entry_point.py
  -> PySide2 / qtpy 获取 Maya main window
  -> QDialog 或 QDockWidget
  -> AuroraView QtWebView
  -> 加载 portfolio React dist
  -> bind_api 暴露 Maya 工具能力
  -> React UI 调 auroraview.api.*
  -> Maya 场景操作 / 检查 / 写 attr / 导出 report
```

第一阶段不要急着把 5 个模块全部搬进去。先选一个真正 DCC 感最强的模块做 vertical slice：

1. `Asset Protocol Workbench`
   - Maya 中创建 synthetic asset。
   - 读取选择对象。
   - 写 custom attr / vertex color / UV payload mock。
   - 前端显示协议字段、风险、导出 JSON。

2. `Cross-DCC Rule Matrix`
   - Maya 中跑 Pyblish 风格 Collect / Validate / Fix / Extract。
   - 前端只负责规则矩阵和 fix preview。
   - Python 保持确定性检查逻辑。

3. `Visual Review Studio`
   - Maya 中固定相机和 pass capture。
   - 前端显示 pass matrix / diff report。

`Task Orchestrator` 继续作为平台层/证据层，不再优先做主展示。

## 五.关键风险

1. 环境风险  
   本地源码直接 import 缺少编译产物 `_core.pyd`，普通 Python 里也没有 `qtpy`。实际 Maya 验证应使用：

   ```powershell
   "C:\Program Files\Autodesk\Maya2024\bin\mayapy.exe" -m pip install auroraview[qt]
   ```

   或本地 maturin build 后安装 wheel。

2. Maya Qt 版本风险  
   Maya 多数版本使用 PySide2，AuroraView 通过 `qtpy` 适配。需要在目标 Maya 版本里验证 `QtWebView` 是否能稳定显示、关闭、resize、reload。

3. WebView2 运行时风险  
   Windows 下依赖 WebView2。现代 Windows 通常已有，但展示机需要确认。

4. UI 语义风险  
   不能只把 Web dashboard 塞进 Maya。迁移后按钮必须真正调用 Maya API，否则只是“在 Maya 里打开网页”。

5. 本地资源路径风险  
   Vite 默认绝对路径必须修正。建议先 `base: './'`，稳定后再评估 `asset_root` / `auroraview://`。

## 六.下一轮开发计划

### R9.0：DCC Host Layer 最小闭环

- 新建 `dcc-hosts/maya` 或 `showcases/maya-auroraview-host`。
- 写 Maya shelf/entry 脚本。
- 用 `QtWebView` 加载当前 portfolio `dist/index.html`。
- 修正 Vite `base: './'`。
- 在 Maya 内显示当前 UI。

### R9.1：Maya API Bridge

- 前端增加 AuroraView runtime adapter。
- Python 侧绑定：
  - `scene.get_selection`
  - `asset.inspect_protocol`
  - `asset.apply_protocol_payload`
  - `report.export_json`
- React 侧从纯 fixture 改成“fixture / live Maya selection”双模式。

### R9.2：Asset Protocol DCC 化

- 做 Maya synthetic scene。
- 将协议字段写入 custom attrs 或 mock payload。
- 前端展示 before/after、风险、导出 report。
- 截图证据从浏览器改成 Maya 内窗口截图。

### R9.3：Cross-DCC Rule Matrix DCC 化

- 在 Maya 里跑规则检查。
- 将检查结果推给前端。
- 实现 fix preview，不直接破坏场景。

## 七.当前判断

方案可行性：高。

优先级：应立即把后续开发主线从 Web workbench 扩展切换为 `DCC-first + AuroraView host`。

最小验证目标：在 Maya 中打开一个 AuroraView 面板，加载当前 portfolio dist，并完成一个按钮从前端调用 `cmds.ls(selection=True)` 返回结果。
