# Description:
# This R script analyzes the expected goal (xG) contribution of Argentina's football players during the 2022 FIFA World Cup.

# Load necessary libraries
library(tidyverse)
library(StatsBombR)

# Retrieve competition and match data for the FIFA World Cup 2022 involving Argentina
Comp <- FreeCompetitions() %>% filter(competition_name == "FIFA World Cup" & season_name == "2022")
Matches <- FreeMatches(Comp) 
ArgMatch <- Matches %>% filter(home_team.home_team_name == "Argentina" | away_team.away_team_name == "Argentina")

# Extract events data for Argentina matches and format the timestamp
ArgEvents <- free_allevents(MatchesDF = ArgMatch, Parallel = TRUE)
ArgEvents <- formatelapsedtime(ArgEvents)

# Clean the data to remove any inconsistencies
ArgEvents <- allclean(ArgEvents)

# Extract xG data for shots and filter relevant columns
xGA <- ArgEvents %>% filter(type.name == "Shot") %>%
  select(shot.key_pass_id, xGA = shot.statsbomb_xg)

# Join xG data with shot assists data for Argentina
shot_assists <- left_join(ArgEvents, xGA, by = c("id" = "shot.key_pass_id")) %>%
  select(team.name, player.name, player.id, type.name, pass.shot_assist, pass.goal_assist, xGA) %>%
  filter(team.name == "Argentina") %>%
  filter(pass.shot_assist == TRUE | pass.goal_assist == TRUE)

# Calculate xG sum for each player
player_XGA <- shot_assists %>% 
  group_by(player.name, player.id, team.name) %>%
  summarise(xGA = sum(xGA, na.rm = TRUE))

# Calculate xG sum, xG assisted, and xG+xGA for each player
player_xG <- ArgEvents %>% 
  filter(type.name == "Shot") %>%
  filter(shot.type.name != "Penalty" | is.na(shot.type.name)) %>%
  group_by(player.name, player.id, team.name) %>%
  summarise(xG = sum(shot.statsbomb_xg, na.rm = TRUE)) %>%
  left_join(player_XGA) %>%
  mutate(xG_xGA = sum(xG + xGA, na.rm = TRUE))

# Calculate total minutes played for each player
player_minutes <- get.minutesplayed(ArgEvents)

player_minutes <- player_minutes %>% 
  group_by(player.id) %>%
  summarise(minutes = sum(MinutesPlayed))

# Calculate xG, xGA, and xG+xGA per 90 minutes
player_xG_XGA <- left_join(player_xG, player_minutes) %>%
  mutate(nineties = minutes/90,
         xG_90 = round(xG / nineties, 2),
         xGA_90 = round(xGA / nineties, 2),
         xG_xGA90 = round(xG_xGA / nineties, 2))

# Create a chart with top 15 players based on xG_xGA per 90 minutes
chart <- player_xG_XGA %>% 
  ungroup() %>%
  filter(minutes >= 600) %>%
  top_n(n = 15, w = xG_xGA90)

# Reshape the data for plotting
chart <- chart %>%
  select(1, 9:10) %>%
  pivot_longer(-player.name, names_to = "variable", values_to = "values") %>%
  filter(variable == "xG_90" | variable == "xGA_90")

# Plot the chart using ggplot2
ggplot(chart, aes(x = reorder(player.name, values), y = values, fill = fct_rev(variable))) +
  geom_bar(stat = "identity", colour = "white") +
  labs(title = "Expected Goal Contribution", subtitle = "Argentina World Cup, 2022",
       x = "", y = "Per 90", caption = "Minimum 600 Minutes\nNpxG = Value of shots taken (no penalties)\nXG assisted = Value of shots assisted") +
  theme(axis.title.y = element_text(size = 8, color = "#333333", family = "Source Sans Pro"),
        axis.text.x = element_text(size = 8, color = "#333333", family = "Source Sans Pro"),
        axis.ticks = element_blank(),
        panel.background = element_rect(fill = "white", colour = "white"),
        plot.background = element_rect(fill = "white", colour = "white"),
        panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
        plot.title = element_text(size = 12, color = "#333333", family = "Source Sans Pro" , face = "bold"),
        plot.subtitle = element_text(size = 8, color = "#333333", family = "Source Sans Pro", face = "bold"),
        plot.caption = element_text(color = "#333333", family = "Source Sans Pro", size = 5),
        text = element_text(family = "Source Sans Pro"),
        legend.title = element_blank(),
        legend.text = element_text(size = 8, color = "#333333", family = "Source Sans Pro"),
        legend.position = "bottom") +
  scale_fill_manual(values = c("#3371AC", "#DC2228"), labels = c("xG Assisted", "NPxG")) +
  scale_y_continuous(expand = c(0, 0), limits = c(0, max(chart$values) + 0.3)) +
  coord_flip() + 
  guides(fill = guide_legend(reverse = TRUE))
