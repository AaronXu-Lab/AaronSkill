# CSV 数据结构

这个技能只使用 Python 标准库。数据目录为当前项目目录下的 `<project-directory>/data/aw-mail-read-later/`，不是技能目录或全局软链目录。

第一次触发推荐或处理流程时，必须先运行以下幂等命令；如果目录或 CSV 文件缺失，命令会创建它们，如果已经存在则保留原内容：

```bash
python3 <skill-directory>/scripts/read_later_index.py init --data-dir <project-directory>/data/aw-mail-read-later
```

初始化或读取失败时，停止本次推荐，不要只在内存中临时保存记录。

如果技能目录下存在旧版 `data/`，不要自动与项目索引混用。只有用户明确同意时才迁移旧 CSV；项目索引已有文件时不要覆盖，迁移成功前不要删除旧文件。

## `articles.csv`

`articles.csv` 是历史文件名，实际按一行一个规范化内容 URL 记录所有内容类型。将邮件中发现的原始 URL 保存在 `original_url`，将当前保留的来源邮件保存在 `source_email_id`。

| 列 | 含义 |
| --- | --- |
| `canonical_url` | 用于识别和去重的规范化 URL。 |
| `original_url` | 保留邮件中的原始 URL。 |
| `title` | 内容名称或标题（如果能获取）。 |
| `content_type` | 内容类型，例如 `article`、`repository`、`post`、`thread`、`documentation`、`project`、`video` 或 `other`。 |
| `source_email_id` | 当前保留邮件的 Outlook message ID。 |
| `source_email_subject` | 当前保留邮件的主题。 |
| `source_sender` | 当前保留邮件的发件人。 |
| `source_received_at` | Outlook 收件时间。 |
| `source_folder` | 通常为 `Read Later`。 |
| `article_published_at` | 内容发布时间或更新时间；字段名沿用旧版本以保持兼容。 |
| `estimated_minutes` | 预计阅读或浏览时间，使用数字记录。 |
| `word_count` | 可读取的字数、字符数或其他长度数值（如果能获取）。 |
| `first_seen_at` | URL 首次进入本地索引的时间。 |
| `last_checked_at` | 最近一次成功或失败的网页检查时间。 |
| `status` | 生命周期状态，见下文。 |
| `status_reason` | 跳过、失败、排除或删除的简短原因。 |
| `status_updated_at` | 最近一次状态变化时间。 |
| `skip_count` | 用户明确暂时跳过的次数。 |
| `recommendation_count` | 被推荐的次数。 |
| `last_recommended_at` | 最近一次被推荐的时间。 |
| `last_feedback_at` | 最近一次收到反馈的时间。 |
| `feedback_count` | 反馈记录数量。 |
| `selected_at` | 成为当前推荐内容的时间。 |
| `duplicate_email_ids` | 较早重复邮件的 ID，用 `;` 分隔。 |
| `archived_at` | 来源邮件移动到 `Archive` 的时间。 |
| `deleted_at` | 来源邮件移动到 `Deleted Items` 的时间。 |

使用以下状态：

- `new`：符合推荐条件，尚未被推荐；
- `skipped`：暂时跳过，之后仍可再次推荐；
- `recommended`：当前正在推荐的内容；
- `archived`：用户确认完成，来源邮件已经移动到 `Archive`；
- `unavailable_pending_confirmation`：页面访问失败，正在等待用户确认是否删除；
- `unavailable`：页面访问失败，邮件仍在 `Read Later`，但排除出推荐；
- `deleted`：用户明确排除或确认后，邮件已经移动到 `Deleted Items`；
- `duplicate_deleted`：较早的重复邮件已经移动到 `Deleted Items`。

刷新内容元数据时，不要静默覆盖 `status`、`status_reason` 或状态时间。只有工作流动作可以改变生命周期状态。

## `feedback.csv`

每次明确的用户反馈追加一行，不要覆盖旧记录：

| 列 | 含义 |
| --- | --- |
| `feedback_at` | 反馈发生的时间。 |
| `canonical_url` | 相关的内容 URL（如果有）。 |
| `email_id` | 相关的 Outlook message ID（如果有）。 |
| `signal` | 简短的归一化信号，例如 `positive`、`negative`、`too_long`、`useful`、`skip` 或 `exclude`。 |
| `feedback_text` | 原样保存的用户反馈。 |
| `context_snapshot` | 反馈发生时的请求或上下文简述。 |
| `time_context` | 当地时间和星期信息。 |

将近期、重复出现且明确表达的反馈视为比单次推断出的跳过更强的偏好证据。不要把普通的暂时跳过自动变成永久排除。
