/**
 * 流程画布的数据模型：节点四类、边三类，出口与场景切换挂在节点上，流程最多两级。
 * `TTarget` 是项目自己的“预览目标”（例如 `{ screen, scenario }`），画布只负责把它交给 `previewSrc` 生成地址。
 */
export enum ENodeKind { screen = 'screen', decision = 'decision', reference = 'reference', note = 'note' }
export enum EEdgeKind { main = 'main', branch = 'branch', fault = 'fault' }
/** 连线筛选：默认项「全部」排第一位。 */
export enum EEdgeFilter { all = 'all', main = 'main', fault = 'fault' }
export const EDGE_FILTER_LABELS: Record<EEdgeFilter, string> = { [EEdgeFilter.all]: '全部', [EEdgeFilter.main]: '主路径', [EEdgeFilter.fault]: '仅异常分支' }
export enum EEdgeTone { strong = 'strong', faded = 'faded', hidden = 'hidden' }

/** 返回、取消不画常驻线，写在卡片底栏；重新发送这类原地操作页面上已经很直白，不列为出口。`to` 是目标页面标题。 */
export interface ICanvasExit { label: string; to: string }
/** 同一页面的几种结果合并为一个节点，在底栏切换；第一项与节点的 `target` 相同。 */
export interface ICanvasVariant<TTarget> { label: string; target: TTarget }

export interface ICanvasNodeData<TTarget> extends Record<string, unknown> {
  kind: ENodeKind
  title: string
  /** 无入边的节点必须是入口：单行短名称，进入条件写进 `detail`。 */
  entry?: string
  /** 页面卡片：点 info 打开的说明；判断节点：直接显示的判断依据；说明节点：折叠的正文。 */
  detail?: string
  exits?: ICanvasExit[]
  target?: TTarget
  variants?: ICanvasVariant<TTarget>[]
  /** 引用节点指向的流程 ID。 */
  link?: string
}
export interface ICanvasNodeDef<TTarget> extends ICanvasNodeData<TTarget> { id: string }
export interface ICanvasEdgeDef { id: string; source: string; target: string; label: string; kind: EEdgeKind }
/** `parent` 是引用它的上级流程，用于目录分组；流程最多两级，子流程不再有子流程。 */
export interface ICanvasFlowDef<TTarget> {
  label: string
  parent?: string
  /** 单流程预览（`?preview={flow}`）从这里开始。 */
  preview: TTarget
  nodes: ICanvasNodeDef<TTarget>[]
  edges: ICanvasEdgeDef[]
}
export type TCanvasFlows<TTarget> = Record<string, ICanvasFlowDef<TTarget>>

/** 直接子流程；不传父流程时返回顶层流程。 */
export function flowChildren<TTarget>(flows: TCanvasFlows<TTarget>, parent?: string): string[] {
  return Object.keys(flows).filter((id) => flows[id].parent === parent)
}

/** 数据定义用的小工厂：主路径节点先声明，布局会把它们排在每层最上方。 */
type TExtra<TTarget> = Pick<ICanvasNodeData<TTarget>, 'entry' | 'detail' | 'exits' | 'variants'>
export const screen = <T>(id: string, title: string, target: T, extra: TExtra<T> = {}): ICanvasNodeDef<T> => ({ id, kind: ENodeKind.screen, title, target, ...extra })
export const decision = <T>(id: string, title: string, extra: TExtra<T> = {}): ICanvasNodeDef<T> => ({ id, kind: ENodeKind.decision, title, ...extra })
export const reference = <T>(id: string, title: string, link: string, extra: TExtra<T> = {}): ICanvasNodeDef<T> => ({ id, kind: ENodeKind.reference, title, link, ...extra })
export const note = <T>(id: string, title: string, detail: string): ICanvasNodeDef<T> => ({ id, kind: ENodeKind.note, title, detail })
export const edge = (source: string, target: string, label: string, kind = EEdgeKind.branch): ICanvasEdgeDef => ({ id: `${source}-${target}`, source, target, label, kind })
export const mainEdge = (source: string, target: string, label: string) => edge(source, target, label, EEdgeKind.main)
export const faultEdge = (source: string, target: string, label: string) => edge(source, target, label, EEdgeKind.fault)
export const exit = (label: string, to: string): ICanvasExit => ({ label, to })
