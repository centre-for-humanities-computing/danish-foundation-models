library(tidyverse)
library(lubridate)

domains <- read_csv("../../../data/domain_counts.csv")
domains$X1 <- NULL
colnames(domains) <- c("domain", "frequency")

top_domains <- domains %>%
  arrange(desc(frequency)) %>%
  head(50)

# Count of top domains
ggplot(top_domains, aes(reorder(domain, -frequency), frequency)) +
  geom_bar(stat = "identity") +
  coord_flip() +
  labs(x = "Domains", y = "Frequency") +
  scale_y_continuous(
    labels = function(x) format(x, scientific = FALSE, big.mark = ",")
  ) +
  theme_minimal() +
  theme(
    text = element_text(size = 14),
    panel.grid.major = element_blank(),
    panel.grid.minor = element_blank(),
    panel.border = element_blank(),
    panel.background = element_blank(),
  )

ggsave("../../../docs/desc_stats/netarkivet_top_50_domains.png")


# Count of domains
times <- read_csv("../../../data/timestamp_counts.csv")
times$X1 <- NULL
colnames(times) <- c("time", "frequency")

times$date <- ymd(times$time) # convert to year month date
times$month_year <- ym(format(as.Date(times$date), "%Y-%m"))


times %>%
  group_by(month_year) %>%
  summarise(frequency = sum(frequency)) %>%
  ggplot(aes(month_year, frequency)) +
  geom_point() +
  labs(x = "Date Collected", y = "Sites Collected") +
  scale_y_continuous(
    labels = function(x) format(x, scientific = FALSE, big.mark = ",")
  ) +
  theme_minimal() +
  theme(
    text = element_text(size = 14),
    panel.grid.major = element_blank(),
    panel.grid.minor = element_blank(),
    panel.border = element_blank(),
    panel.background = element_blank(),
  )

ggsave("../../../docs/desc_stats/netarkivet_sites_over_time.png")