USE voters;

CREATE TABLE `img_dataset` (
  `img_id` int(11) NOT NULL,
  `img_person` varchar(3) NOT NULL
) ;
 
CREATE TABLE `voters` (
  `voter_nic` varchar(3) NOT NULL,
  `voter_name` varchar(50) NOT NULL,
  `voter_added` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP
);
 
ALTER TABLE `img_dataset`
  ADD PRIMARY KEY (`img_id`);
 
ALTER TABLE `voters`
  ADD PRIMARY KEY (`voter_nic`);