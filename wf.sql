CREATE TABLE `UserMaster` (
  `id` integer PRIMARY KEY AUTOINCREMENT,
  `role` varchar(255),
  `username` varchar(255),
  `password` varchar(255)
);

CREATE TABLE `Workflow` (
  `id` integer PRIMARY KEY AUTOINCREMENT,
  `name` varchar(255),
  `customNotification` varchar(255),
  'numofstages' integer,
  'admin_id' integer,
  FOREIGN KEY (`admin_id`) REFERENCES `UserMaster` (`id`)

);

CREATE TABLE `Stage` (
  `id` integer PRIMARY KEY AUTOINCREMENT,
  `workflow_id` integer,
  `name` varchar(255),
  'numberofactions' integer,

 FOREIGN KEY (`workflow_id`) REFERENCES `Workflow` (`id`)
);

CREATE TABLE `Action` (
  `id` integer PRIMARY KEY AUTOINCREMENT,
  `stage_id` integer,
  `name` varchar(255),
FOREIGN KEY (`stage_id`) REFERENCES `Stage` (`id`)
);

CREATE TABLE `StageTransition` (
  `prev_stage` integer,
  `action` integer,
  `next_stage` integer,
FOREIGN KEY (`prev_stage`) REFERENCES `Stage` (`id`),
FOREIGN KEY (`action`) REFERENCES `Action` (`id`),
FOREIGN KEY (`next_stage`) REFERENCES `Stage` (`id`)
);

CREATE TABLE `WorkflowInstance` (
  `id` integer PRIMARY KEY AUTOINCREMENT,
  `workflow_id` integer,
FOREIGN KEY (`workflow_id`) REFERENCES `Workflow` (`id`)

);

CREATE TABLE `StageActorInstance` (
  `stage_id` integer,
  `user_id` integer,
  `workflow_instance_id` integer,
FOREIGN KEY (`stage_id`) REFERENCES `Stage` (`id`),
FOREIGN KEY (`user_id`) REFERENCES `UserMaster` (`id`),
FOREIGN KEY (`workflow_instance_id`) REFERENCES `WorkflowInstance` (`id`)
);

CREATE TABLE `StageInstance` (
  `id` integer PRIMARY KEY AUTOINCREMENT,
	'stage_actor' integer,
  `workflow_instance_id` integer,
  `current_stage_id` integer,
  `action` integer,
FOREIGN KEY (`workflow_instance_id`) REFERENCES `WorkflowInstance` (`id`),
FOREIGN KEY (`current_stage_id`) REFERENCES `Stage` (`id`)
FOREIGN KEY (`stage_actor`) REFERENCES `StageActorInstance` (`user_id`)
FOREIGN KEY (`action`) REFERENCES `Action` (`id`)
);
