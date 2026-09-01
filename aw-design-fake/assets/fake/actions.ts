// aw-design-fake:managed-start
import { notify } from './adapter'
import { FAKE_DATA } from './data'

/**
 * 后端能力缺失时的统一占位提示。文案只来自同目录 `data.ts`，提示的具体呈现由项目自有的
 * `adapter.ts` 决定；接上真实接口时删掉调用即可，看到这条提示就说明该入口还没接后端。
 */
export function showFakeSonner() {
  notify(FAKE_DATA.sonner)
}
// aw-design-fake:managed-end
