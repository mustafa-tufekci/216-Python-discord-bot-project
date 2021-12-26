CREATE TABLE IF NOT EXISTS guilds(
	GuildID integer PRIMARY KEY,
	Prefix text DEFAULT "!"
);

CREATE TABLE IF NOT EXISTS exp (
	UserID integer PRIMARY KEY,
	XP integer DEFAULT 0,
	Level integer DEFAULT 0,
	XPLock text DEFAULT CURRENT_TIMESTAMP
);

-- Muting and unmuting members - Building a discord.py bot - Part 21
-- CREATE TABLE IF NOT EXISTS mutes (
-- 	UserID integer PRIMARY KEY,
-- 	RoleIDs text,
-- )

CREATE TABLE IF NOT EXISTS starboard (
	RootMessageID integer PRIMARY KEY,
	StarMessageID integer,
	Stars integer DEFAULT 1
);