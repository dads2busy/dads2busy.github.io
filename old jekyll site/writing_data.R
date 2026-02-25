library(data.table)
library(yaml)
library(readr)
library(stringr)

get_yaml <- function(file_path = "writing/_posts/1996-04-01-politicize.md") {
  dashes_loc <- str_locate_all(read_file(file_path), "---")
  yml_end <- dashes_loc[[1]][length(dashes_loc[[1]])]
  yml <- str_sub(read_file(file_path), 1, yml_end)
  read_yaml(text = yml)
}

clean_html <- function(htmlString) {
  return(gsub("<.*?>", "", htmlString))
}

get_description <- function(file_path = "writing/_posts/1996-04-01-politicize.md") {
  dashes_loc <- str_locate_all(read_file(file_path), "---")
  desc_start <- dashes_loc[[1]][length(dashes_loc[[1]])] + 1
  clean_html(str_replace_all(str_sub(read_file(file_path), desc_start), "\n", ""))
}



file_paths <- list.files("writing/_posts/", pattern = "*.md$", full.names = TRUE)

if (exists("dt_all")) rm("dt_all")
for (f in file_paths) {
  yml <- get_yaml(f)
  desc <- get_description(f)

  dt <- data.table(
    category = yml$category,
    subcategory = yml$subcategory,
    title = yml$title,
    pub_year = yml$date,
    publisher = yml$sponsor,
    award = yml$award,
    role = yml$role,
    authors = yml$authors,
    pages = yml$pages,
    editors = yml$editors,
    website = yml$website,
    doi = yml$DOI,
    subcategory_ordinal = yml$ordinal,
    description_long = desc,
    description_short = ""
  )

  if (exists("dt_all")) dt_all <- rbindlist(list(dt_all, dt), use.names = TRUE, fill = TRUE)
  else dt_all <- dt
}



res_dt <- data.table(
    category = "research",
    subcategory = "Data Integration & Management",
    title = "Virginia Longitudinal Data System Expansion - Linking to Workforce and Postsecondary",
    record_date = "2012-05-22 16:25:06 -0700",
    sponsor = "U.S. Department of Education",
    award = "$1,760,000",
    award_years = "2010-2013",
    role = "PI",
    website = "https://myvlds.virginia.gov/",
    report1 = "VT-VLDS Lexicon Specifications v1.pdf",
    report2 = "VT-VLDS Lexicon Metadata Tool Design Document.pdf",
    report3 = "VT-VLDS Shaker Specifications v2.pdf",
    report4 = "VT-VLDS Shaker Database Model.pdf",
    report5 = "VT-VLDS Data Adapter User Guide.pdf",
    report6 = "VT-VLDS Identity Resolution and Query Execution Process Overview.pdf",
    media1link = "",
    media1title = "",
    media2link = "",
    media2title = "",
    media3link = "",
    media3title = "",
    subcategory_ordinal = 2,
    description_long = "Working with the Virginia Department of Education (VDOE), the Virginia Information Technologies Agency (VITA), the State Council of Higher Education (SCHEV), the Virginia Community College System, and Virginia’s workforce agencies on a $17.5 million grant to establish a comprehensive, longitudinal P-20 data system, including: creation of an integrated K-12 student-teacher information system; creation of a longitudinal data linking and reporting system; development of a web-based portal to access education and workforce data; design of a data management and control system; and development of a secure mechanism for post-secondary institutions to receive high school transcripts in the form of electronic data.",
    description_short = ""
)


