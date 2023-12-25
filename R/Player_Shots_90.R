# Description: 
# Analyzing shots and goals data for top Argentine players in FIFA World Cup 2022.

# Load required libraries
library(ggplot2)

# Fetch competitions data for FIFA World Cup 2022
Comp <- FreeCompetitions() %>% filter(competition_name == "FIFA World Cup" & season_name == "2022")

# Fetch matches data for the specified competition
Matches <- FreeMatches(Comp)

# Filter matches involving Argentina
argMatch <- Matches %>% filter(home_team.home_team_name == "Argentina" | away_team.away_team_name == "Argentina")

# Retrieve all events for Argentina matches, parallelize for efficiency, and format elapsed time
argMatch <- free_allevents(MatchesDF = argMatch, Parallel = TRUE)
argMatch <- formatelapsedtime(argMatch)

# Calculate shots and goals per player
player_shots <- argMatch %>% 
  group_by(player.name, player.id) %>%
  summarise(shots = sum(type.name == "Shot", na.rm = TRUE),
            goals = sum(shot.outcome.name == "Goal", na.rm = TRUE))

# Calculate total minutes played per player
player_minutes <- get.minutesplayed(argMatch) %>%
  group_by(player.id) %>%
  summarise(minutes = sum(MinutesPlayed))

# Merge shots and minutes data
player_shots <- left_join(player_shots, player_minutes)

# Calculate metrics per 90 minutes
player_shots <- player_shots %>% 
  mutate(nineties = minutes / 90,
         shots_per90 = shots / nineties)

# Arrange data by shots per 90 in descending order
player_shots <- player_shots %>% 
  arrange(desc(shots_per90))

# Filter for players with goals and at least 90 minutes played
player_shots <- player_shots %>% 
  filter(goals > 0) %>%
  filter(nineties > 1)

# Select the top 10 players
top_10 <- player_shots %>% 
  head(10)

# View the top 10 players
view(top_10)

# Create a bar plot showing Shots Per 90 for the top 10 players
ggplot(data = top_10, aes(x = reorder(player.name, shots_per90), y = shots_per90, fill = shots_per90)) +
  geom_bar(stat = "identity", width = 0.5) +
  geom_text(aes(label = paste("Goals:", goals)), vjust = 0.55, color = "black", size = 3, hjust = 1) +
  
  labs(
    title = "Top 10 Argentine Players - Shots Per 90min", 
    y = "Shots per 90min",
    subtitle = "FIFA World Cup 2022",
    caption = "Data Source: StatsBomb"
  ) +
  
  scale_fill_gradient(low = "red", high = "green") +
  theme(
    axis.title.y = element_blank(), 
    axis.text.y.left = element_text(size = 7)
  ) +
  scale_y_continuous(expand = c(0, 0.05)) +
  coord_flip()
