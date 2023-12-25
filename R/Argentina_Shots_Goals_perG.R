# Description: This code analyzes shots and goals per game for Argentina in the 2022 FIFA World Cup.

# Load necessary libraries
library(ggplot2)

# Filter competitions for FIFA World Cup 2022
Comp <- FreeCompetitions() %>%
  filter(competition_name == "FIFA World Cup" & season_name == "2022")

# Retrieve matches for the specified competition
Matches <- FreeMatches(Comp)

# Filter matches involving Argentina
argMatch <- Matches %>%
  filter(home_team.home_team_name == "Argentina" | away_team.away_team_name == "Argentina")

# Extract all events data for Argentina matches
argMatch <- free_allevents(MatchesDF = argMatch, Parallel = TRUE)

# Clean the data
argMatch <- allclean(argMatch)

# Calculate shots and goals per game for each team
shots_goals <- argMatch %>%
  group_by(team.name) %>%
  summarise(
    shots = sum(type.name == "Shot", na.rm = TRUE) / n_distinct(match_id),
    goals = sum(shot.outcome.name == "Goal", na.rm = TRUE) / n_distinct(match_id)
  )

# Create a bar plot for shots per game
ggplot(data = shots_goals, aes(x = reorder(team.name, shots), y = shots, fill = shots)) +
  geom_bar(stat = "identity", width = 0.5) +
  geom_text(aes(label = paste("Goals per Game:", round(goals, digits = 2))),
            vjust = 0.55, color = "black", size = 3, hjust = 1) +
  labs(title = "Argentina vs WC Opponents - Shots per Game", y = "Shots") +
  scale_fill_gradient(low = "red", high = "green") +
  theme(axis.title.y = element_blank(), plot.title = element_text(hjust = 0.5, size = 10)) +
  scale_y_continuous(expand = c(0, 0.25)) +
  coord_flip()
