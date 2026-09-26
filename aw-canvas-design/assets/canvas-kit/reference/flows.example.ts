import { decision, exit, faultEdge, mainEdge, edge, note, reference, screen, type TCanvasFlows } from './types'

/**
 * 示例流程数据（去掉业务后的最小形态），新项目复制后替换为自己的流程：
 * - 主路径节点先声明；流程最多两级（子流程写 `parent`）；以一个业务段落为一条流程。
 * - 同一页面的多种结果写成 `variants`，不拆成多个节点；返回、取消写成 `exits`，原地操作不列。
 * - 无入边的节点必须带 `entry`。
 */
export interface IDemoTarget { screen: string; scenario?: string }

export const FLOWS: TCanvasFlows<IDemoTarget> = {
  main: {
    label: '主流程',
    preview: { screen: 'account' },
    nodes: [
      screen('account', '输入账号', { screen: 'account' }, { entry: '/login', detail: '邮箱或手机号均可' }),
      screen('credentials', '密码与验证方式', { screen: 'credentials' }, {
        variants: [{ label: '有密码', target: { screen: 'credentials' } }, { label: '无密码账号', target: { screen: 'credentials', scenario: 'no-password' } }],
      }),
      decision('route', '登录后去哪里？', { detail: '登录成功后，按组织状态分流' }),
      screen('workspace', '工作台', { screen: 'workspace' }, { exits: [exit('退出登录', '输入账号')] }),
      screen('otp', '邮箱验证码', { screen: 'otp' }, { exits: [exit('修改邮箱', '输入账号')] }),
      screen('invalid', '验证入口不可用', { screen: 'invalid' }, { exits: [exit('重新申请', '密码与验证方式'), exit('返回登录', '输入账号')] }),
      reference('registration', '注册', 'registration'),
      note('channel', '渠道页回跳', '跳转目标是合作渠道页时，成功后直接返回渠道页。'),
    ],
    edges: [
      mainEdge('account', 'credentials', '继续'), mainEdge('credentials', 'route', '密码正确'), mainEdge('route', 'workspace', '有当前组织'),
      edge('account', 'registration', '注册'), edge('account', 'otp', '验证码登录'), edge('otp', 'route', '验证通过'),
      faultEdge('otp', 'invalid', '验证码失效'), edge('route', 'channel', '渠道目标'),
    ],
  },
  registration: {
    label: '注册',
    parent: 'main',
    preview: { screen: 'register' },
    nodes: [
      screen('register', '填写注册邮箱', { screen: 'register' }, { entry: '注册', exits: [exit('登录', '输入账号')] }),
      screen('sent', '查收注册邮件', { screen: 'sent' }),
      reference('route', '登录后分流', 'main'),
    ],
    edges: [mainEdge('register', 'sent', '发送链接'), mainEdge('sent', 'route', '邮箱验证通过')],
  },
}
