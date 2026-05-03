

-- Custom fields breakdown
WITH customfields AS (


-- Unnest the customfields array so each task/custom field is a row
WITH unnested AS (
  SELECT
    t.*,
    cf.id AS customfield_id,
    cf.value AS customfield_value,
    l.title AS customfield_name
  FROM PROJECT.DATASET.wrike_tasks_v4 t
  CROSS JOIN UNNEST(t.customfields) AS cf
  -- Join to lookup table to get custom field names instead of IDs
  LEFT JOIN PROJECT.DATASET.wrike_custom_fields_v4 l
    ON cf.id = l.id
)


-- Re-aggregate back to one row per task
SELECT
  id,
  ANY_VALUE(title) title,
  ANY_VALUE(status) status,
  ANY_VALUE(createddate) created_date,
  ANY_VALUE(completeddate) completed_date,
  ANY_VALUE(dates.start) start_date,
  ANY_VALUE(dates.due) due_date,
  ANY_VALUE(permalink) permalink,
  ANY_VALUE(effortallocation) effort,
  -- Rebuild custom fields into an array of structs per task
  ARRAY_AGG(
    STRUCT(
      customfield_name AS name,
      customfield_value AS value
    )
  ) custom_field
FROM unnested
GROUP BY id
),




-- Authors breakdown
authors AS (


-- Unnest author IDs to get one row per task-author
WITH unnested AS (
  SELECT
    t.id,
    CONCAT(l.firstname, " ", l.lastname) AS name
  FROM PROJECT.DATASET.wrike_tasks_v4 t
-- Join on users table to get user’s name associated instead of user ID
  JOIN PROJECT.DATASET.wrike_contacts_v4 l
    ON l.id IN UNNEST(t.authorids)
)


-- Re-aggregate authors into array per task
SELECT
  id,
  ARRAY_AGG(name) author_name
FROM unnested
GROUP BY id
),




-- Assignees breakdown
assignees AS (


-- Unnest responsible IDs to get one row per task-assignee
WITH unnested AS (
  SELECT
    t.id,
    CONCAT(l.firstname, " ", l.lastname) AS name
  FROM PROJECT.DATASET.wrike_tasks_v4 t
-- Join on users table to get names instead of user IDs
  JOIN PROJECT.DATASET.wrike_contacts_v4 l
    ON l.id IN UNNEST(t.responsibleids)
)


-- Re-aggregate assignees into array per task
SELECT
  id,
  ARRAY_AGG(name) AS assignee_names
FROM unnested
GROUP BY id
),




-- Time and effort breakdown
effort AS (


-- Join time logs to tasks and users
WITH time_entries AS (
  SELECT
    tl.taskid,
    t.title,
    t.permalink,
    tl.userid,
    CONCAT(c.firstname, " ", c.lastname) AS user_name,
    tl.hours,
    ROUND(tl.hours * 60, 0) minutes,
    t.billingtype billing_type,
    tl.createddate created_date,
    tl.updateddate updated_date,
    tl.trackeddate tracked_date,
    tl.comment,
    tl.categoryid
  FROM PROJECT.DATASET.wrike_time_logs_v4 tl
-- Associate time logs with the task details
  LEFT JOIN PROJECT.DATASET.wrike_tasks_v4 t
    ON tl.taskid = t.id
-- Join to assign names to time logs instead of user IDs
  LEFT JOIN PROJECT.DATASET.wrike_contacts_v4 c
    ON tl.userid = c.id
),




-- Aggregate time per user per task
total_user_time_by_task AS (
  SELECT
    taskid,
    ANY_VALUE(title) title,
    ANY_VALUE(permalink) permalink,
    ANY_VALUE(billing_type) billing_type,
    -- Build struct per user summarizing their total time
    STRUCT(
      userid,
      ANY_VALUE(user_name) AS user_name,
      SUM(hours) AS hours,
      SUM(minutes) AS minutes
    ) time_tracked
  FROM time_entries
  GROUP BY taskid, userid
)




-- Aggregate to task level
SELECT
  taskid,
  title,
  permalink,
  billing_type,
  time_tracked.userid,
  time_tracked.user_name,
  time_tracked.hours,
  time_tracked.minutes,
  -- Total minutes logged across all users
  SUM(time_tracked.minutes) OVER (PARTITION BY taskid) as total_task_minutes
FROM total_user_time_by_task
)




-- Final Select
SELECT
c.id,
c.title,
c.permalink,
au.author_name,
a.assignee_names,
status,
created_date,
completed_date,
start_date,
due_date,


-- Allocated effort from task metadata
c.effort.totaleffort AS allocated_effort,


-- Actual logged effort
e.total_task_minutes,
userid,
user_name,
hours,
Minutes,


 -- Pull the client name and team associated with the task
 MAX(IF(cf.name = 'Client List', cf.value, NULL)) AS client_list,
 MAX(IF(cf.name = 'Budget Department', cf.value, NULL)) AS budget_department,


--Over/Under acceptable hours
CASE
WHEN total_task_minutes > (c.effort.totaleffort*1.2) AND total_task_minutes > 0 AND c.effort.totaleffort > 0 THEN 'OVER'
WHEN total_task_minutes < (c.effort.totaleffort*0.8) AND total_task_minutes > 0 AND c.effort.totaleffort > 0 THEN 'UNDER'
WHEN total_task_minutes < (c.effort.totaleffort*1.2) AND total_task_minutes > (c.effort.totaleffort*0.8) AND total_task_minutes > 0 AND c.effort.totaleffort > 0 THEN 'GOOD'
END AS on_time


FROM customfields c


LEFT JOIN UNNEST(c.custom_field) AS cf
LEFT JOIN authors au
ON c.id = au.id
LEFT JOIN assignees a
ON c.id = a.id
LEFT JOIN effort e
ON c.id = e.taskid
GROUP BY ALL








