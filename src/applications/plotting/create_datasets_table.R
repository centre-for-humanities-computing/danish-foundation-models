library(tidyverse)
library(kableExtra)

data_desc = tribble(
  ~Dataset, ~"# Tokens (Billions)", ~"# Tokens after filtering (Billions)", ~"% Low-Quality Documents", ~"% Duplicate Documents", ~"Open Source",
  "DaNews", 9.29                  , 8.67                                  , 0.09                    , 0.04                  , "No",
  "HopeTwitter", 0.97             , 0.48                                  , 0.09                    , 0.33                  , "No",
  "Netarkivet Text", 864.7        , 134                                   , 0.27                    , 0.68                  , "No",
  "DAGW_{DFM}", 1.31              , 0.83                                  , NA                      , NA                    , "Yes",
)

# transposing table
names = data_desc$Dataset
data_desc=as.data.frame(t(data_desc[,1:length(names)+2]))
colnames(data_desc) = names


preprocessing_thresholds = tribble(
~""         , ~"DaNews", ~"HopeTwitter", ~"DAGW_{DFM}", ~"Netarkivet Text",
"Stopwords"            , ">2", ">2", ">2", ">2",
"Mean word length"     , "3-10", "2-14", "3-10", "3-10",
"Document lenth (tokens)", "50-100,000", "10-100,000", "50-100,000","50-100,000",
"Character length"     , "<5,000,000", "<5,000,000", "<5,000,000", "<5,000,000", 
"Alphabetic ratio"     , "<0.6","<0.6", "<0.6", "<0.6",
"Hashtag ratio"        , "<0.1", "-", "<0.1","<0.1",
"Ellipsis ratio"       ,"<0.1", "-", "<0.1","<0.1",
"Lines starting with bullet points","<0.90", "-","<0.90","<0.90",
"Lines ending with ellipsis","<0.30", "-","<0.30","<0.30",
"Duplicate line character fraction", "<0.20", "<0.20","<0.20","<0.20",
"Duplicate paragraph character fraction", "<0.20","<0.20","<0.20","<0.20",
"Top 2-gram character fraction", "<0.20", "<0.20","<0.20","<0.20",
"Top 3-gram character fraction", "<0.18","<0.18","<0.18","<0.18",
"Top 4-gram character fraction", "<0.16", "<0.16","<0.16","<0.16",
"Duplicate 5-gram character fraction", "<0.25", "<0.25","<0.25","<0.25",
"Duplicate 6-gram character fraction", "<0.24", "<0.24","<0.24","<0.24",
"Duplicate 7-gram character fraction", "<0.23", "<0.23","<0.23","<0.23",
"Duplicate 8-gram character fraction", "<0.22", "<0.22","<0.22","<0.22",
"Duplicate 9-gram character fraction", "<0.21", "<0.21","<0.21","<0.21",
"Duplicate 10-gram character fraction", "<0.20", "<0.20","<0.20","<0.20",
)


deduplication_table = tribble(
  ~""           , ~"DaNews", ~"HopeTwitter",~"DAGW_{DFM}", ~"Netarkivet Text",
  "n-gram"                 , "13", "10", "13","13",
  "Jaccard similarity"     , "<80%", "<80%", "<80%","<80%",
  "MinHash permutations"   , "128", "128","128","64",
  "Across", "Entire corpus", "Entire corpus", "Entire corpus", "Each year",
)

deduplication_table %>%  
  kbl(, booktabs = T, caption = "Deduplication Parameters", format="latex")

preprocessing_thresholds %>%  
  kbl(, booktabs = T, caption = "Quality filtering thresholds", format="latex") %>% 
  pack_rows("Heuristic Filters", 1, 9) %>%
  pack_rows("Repititious text removal", 10, 20) %>% 
  kable_styling(latex_options = c("scale_down"))

data_desc %>% select(-`Open Source`)  %>% 
  kbl(, booktabs = T, caption = "Dataset overview", , linesep="", format="latex") %>% 
  kable_styling() #latex_options = c("scale_down"))




tokenization_table = tribble(
~"Subword segmentation", ~"Documents", ~"Vocabulary", ~"Precision", ~"Recall", ~"f1-score", ~"f2-score", ~"Jaccard-index",
"Unigram",               "1x",       55000,         0.72,         0.65,      0.68,       0.66,        0.52,
"BPE",       "1x", 55000,  0.76, 0.58, 0.66, 0.61, 0.49,
"Wordpiece", "1x", 55000,  0.67, 0.58, 0.62, 0.60, 0.45,
"Unigram",   "5x", 55000,  0.71, 0.65, 0.68, 0.66, 0.52,
"Unigram",   "1x", 128000, 0.76, 0.52, 0.62, 0.55, 0.45,
"Unigram",   "1x", 32000,  0.68, 0.75, 0.72, 0.74, 0.56
)
caption="Performance of subword segmentation algorithms on annotated Danish compound splits. 
Documents denote the amount of training documents, with 1x indicate 100.000 documents. 
Group 1 compares the algorithm and Group 2 examines the influence of vocabulary size and training parameters."
tokenization_table %>% 
  kbl(, booktabs = T, caption = caption, linesep="", format="latex") %>% 
  add_header_above(c(" ", "Training parameters" = 2, "Performance metric" = 5)) %>%
  pack_rows("Group 1", 1, 3) %>%
  pack_rows("Group 2", 4, 6) %>% 
  kable_styling(latex_options = c("scale_down"))


