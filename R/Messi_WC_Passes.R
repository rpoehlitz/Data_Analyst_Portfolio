# FIFA World Cup 2022: Messi's Completed Box Passes
# This script analyzes Lionel Messi's completed box passes during the FIFA World Cup 2022.
# It uses StatsBombR and ggplot2 to visualize Messi's passing performance on the pitch.

# Load necessary libraries
library(tidyverse)
library(ggplot2)
library(SBpitch)
library(StatsBombR)

# Retrieve data for the FIFA World Cup 2022
Comp <- FreeCompetitions() %>% filter(competition_name == "FIFA World Cup" & season_name == "2022")
Matches <- FreeMatches(Comp) 

# Filter matches involving Argentina
ArgMatch <- Matches %>% filter(home_team.home_team_name == "Argentina" | away_team.away_team_name == "Argentina")

# Retrieve and clean event data for Argentina matches
ArgEvents <- free_allevents(MatchesDF = ArgMatch, Parallel = TRUE)
ArgEvents = allclean(ArgEvents)

# Filter Messi's completed box passes
passes = ArgEvents %>%  
  filter(
    type.name == "Pass" & 
      is.na(pass.outcome.name) & 
      player.id == 5503
  ) %>% 
  filter(
    pass.end_location.x >= 102 & 
      pass.end_location.y <= 62 & 
      pass.end_location.y >= 18
  )

# Calculate Stats
pass_stats <- passes %>% 
  summarise(
    n=n(),
    yards = mean(pass.length),
    assists = sum(is.na(pass.goal_assist)),
  
  )

# Create a pitch and plot Messi's completed box passes
plot1 <- create_Pitch() +
  geom_segment(
    data = passes,
    aes(
      x = location.x, 
      y = location.y, 
      xend = pass.end_location.x, 
      yend = pass.end_location.y,
      color = pass.length
    ),
    lineend = "round", 
    size = 0.5, 
    arrow = arrow(length = unit(0.07, "inches"), ends = "last", type = "open")
  ) +
  labs(
    title = "Messi, Completed Box Passes", 
    subtitle = "WC, 2022",
    color = "Pass Length (yards)"
  ) + 
  scale_y_reverse() +
  coord_fixed(ratio = 105/100) +
  scale_color_gradient(low = "red", high = "green", na.value = "grey") +
  theme(legend.position = "bottom")  # Optionally, move the legend to the bottom

plot2 <- ggplot(data = pass_stats, mapping = aes(x = "", y = yards)) +
  geom_col() +
  
  
  geom_text(
    aes(label = paste0("Summary Stats")),
    color = "gold",
    vjust = 1,
    size = 4
  ) +
  geom_text(
    aes(label = paste0("Assists: \n", assists)),
    color = "white",
    vjust = 3,
    size = 4
  ) +
  theme(
    text = element_text(size = unit(4, "mm"))  # Adjust the size dynamically
  )

library(cowplot)
plot_grid(plot1,plot2,ncol = 2,rel_widths = c(2,1))
