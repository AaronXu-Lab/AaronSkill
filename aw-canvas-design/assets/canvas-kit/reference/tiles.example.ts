import type { ITileCollection } from './tiles'

/** Illustrative paths / translation keys only; replace with actual evidence.
 * No original component is implemented by this data example.
 */
export const TILE_COLLECTION: ITileCollection<{ component: string; scenario: string }> = {
  mode: 'tiles', id: 'overlays', titleKey: 'canvas.overlays.title',
  scope: { included: ['registered overlays in the selected modules'], excluded: ['unscanned modules'] },
  groups: [
    { id: 'dialogs', titleKey: 'canvas.dialogs', kind: 'dialog' },
    { id: 'sheets', titleKey: 'canvas.sheets', kind: 'sheet' },
  ],
  modules: [
    { id: 'files-dialogs', groupId: 'dialogs', titleKey: 'canvas.modules.files' },
    { id: 'knowledge-sheets', groupId: 'sheets', titleKey: 'canvas.modules.knowledge' },
  ],
  rows: [
    { id: 'confirm-row', moduleId: 'files-dialogs', titleKey: 'canvas.rows.confirm', itemIds: ['confirm-default', 'confirm-result'], sequence: 'verified', evidence: ['Illustrative only: confirm completion opens result; replace with actual call-chain evidence'] },
    { id: 'details-row', moduleId: 'knowledge-sheets', titleKey: 'canvas.rows.details', itemIds: ['details-default'], sequence: 'unverified', evidence: [] },
  ],
  items: [
    {
      id: 'confirm-default', componentId: 'confirm', scenarioId: 'default', moduleId: 'files-dialogs',
      titleKey: 'canvas.confirm.default', change: 'existing',
      source: { path: 'src/confirm.tsx', symbol: 'ConfirmDialog', reachability: 'reachable', evidence: ['src/actions.tsx: ConfirmDialog import and render'] },
      capability: { kind: 'interactive', target: { component: 'confirm', scenario: 'default' },
        viewport: { width: 800, height: 640 }, viewportRule: 'Example only: adapt to original declaration and responsive gutters' },
      verification: { status: 'unverified', evidence: [] },
    },
    {
      id: 'confirm-result', componentId: 'result', scenarioId: 'success', moduleId: 'files-dialogs',
      titleKey: 'canvas.confirm.result', change: 'existing',
      source: { path: 'src/result.tsx', symbol: 'ResultDialog', reachability: 'reachable', evidence: ['Illustrative completion callback; replace with actual evidence'] },
      capability: { kind: 'source-only', reasonKey: 'canvas.preview.adapterMissing' },
      verification: { status: 'unverified', evidence: [] },
    },
    {
      id: 'details-default', componentId: 'details', scenarioId: 'default', moduleId: 'knowledge-sheets',
      titleKey: 'canvas.details.default', change: 'existing',
      source: { path: 'src/details.tsx', symbol: 'DetailsSheet', reachability: 'reachable', evidence: ['src/details-route.tsx: DetailsSheet import and render'] },
      capability: { kind: 'source-only', reasonKey: 'canvas.preview.adapterMissing' },
      verification: { status: 'blocked', evidence: [] },
    },
  ],
}
