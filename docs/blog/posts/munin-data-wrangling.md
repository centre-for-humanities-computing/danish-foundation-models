---
draft: false
date: 2024-01-11
---

# Data wrangling


## DATAHÅNDTERING
Alt dataklargørelse foregår på UCloud. Figur 2 viser den proces alt data skal igennem før det bruges til træning af sprogmodellen. Det rå data arkiveres i sin oprindelige form på UCloud. Derefter annoteres de rå data med metadata.
Dette datasæt overføres til en GPU-accelereret supercomputer igennem en sikker forbindelse, hvorefter selve træningen af modellen begyndes. Under træningen gemmes flere checkpoints med modelvægte. De gemte checkpoints med modelvægte publiceres sammen med modelkode og anvendes til at køre modellen. De tre processor er beskrevet i detalje nedenfor.
 FIGUR XXX: DATAHÅNDTERING

## METADATA OG FORMATERING
Det rå data annoteres med to typer af metadata. Den første type er et datablad (i Markdown, som i HuggingFace datasheets ) der opsummerer hele datasættet og beskriver bl.a. proveniens og hvilken licens der er pålagt det givne datasæt. Et udsnit af et databladseksempel er vist på figur XXX. Den første del af databladet er annoteret i et maskinvenligt format, som gør det muligt at automatisk udvælge datasættet blandt en større samling. Resten af databladet giver en dybere beskrivelse af datasættet i fritekst.
Den anden type af metadata er per-dokument metadata, der beskriver hvilket datasæt dokumentet hører til, hvornår det stammer fra, hvornår det er tilføjet, samt andre metadata f.eks. fra hvilken URL dokumentet kommer fra. Per dokument-metadata gemmes sammen med dokumentet i et standardiseret jsonl format.  Et eksempel på et enkelt dokument inklusiv metadata fra scandi-wiki datasættet  er vist på figur XXX. Disse metadata følger dokumentet igennem hele processeringen, så det er muligt at spore dokumenterne tilbage til kilden fra det endelige træningskorpus. For hvert rå datasæt vedligeholdes et script der kan bruges til konvertering af de rå data til det standardiserede format.
 
FIGUR XXX: DATABLAD-EKSEMPEL 
 FIGUR XXX: EKSEMPEL PÅ ET FORMATERET DOKUMENT MED PER-DOKUMENT METADATA
FILTRERING OG TOKENIZATION
Det standardiserede format muliggør en ensartet processering af dokumenterne. De enkelte filtreringstrin kan inddeles i følgende kategorier:
•	URL-filter
•	Deduplikering
•	Kvalitetsfilter
•	Fjernelse af personoplysninger
De enkelte trin er beskrevet i nedenstående afsnit. Efter filtreringstrinene bliver vores tekstdata tokenized, dvs. konverteret til et binært format der kan læses af modellen.
 
FIGUR XXX: FILTRERING OG TOKENIZATION

## URL-FILTRERING
Data som kommer fra offentlige hjemmesider og dermed har en URL som metadata, bliver først processeret af et URL-filter.
For alle domæner i datasættet hentes domænets robots.txt og ai.txt periodisk. Hvis disse ikke tillader   CommonCrawl eller andre sprogmodel-crawlers tilføjes domænet til en blokeringsliste og dokumenter der stammer fra disse domæner filtreres væk, selv om de pågældende sider måtte være hentet på et tidspunkt, hvor robots.txt/ai.txt ikke blokerede for denne type for crawling.
Derudover anvendes blokeringslister fra forskellige offentligt tilgængelige databaser over skadeligt indhold. Disse lister omfatter bl.a. følgende kategorier:
•	Porno (både via lister og via ord der indgår i domæne-navnet)
•	Phishing
•	Reklamer
•	Kriminelle sider
o	Abuse
o	Fraud
o	Malware
o	Pirat
o	Ransomware
o	Scam
o	Redirect
•	Crypto
•	Drugs
•	Gambling
•	Vaping
•	Social Networks

## KVALITETSFILTER
Web-data kan indeholde meget støj i form a stumper af HTML eller andet kode og ufuldstændige sætninger. Der anvendes forskellige heuristikker, som er baseret på statistik for almindelig tekst, der fanger disse dokumenter af dårlig kvalitet. Vi bruger PT samme filtre som Gopher og C4, men der undersøges også mulighed for filtrering baseret på perpleksitet og andre metrikker.

## DEDUPLIKERING
Deduplikering anvendes til at fjerne gentagelser. Gentagelser i træningsdata kan påvirke modellen i en uønsket retning. Der anvendes to typer af deduplikering linje-deduplikering og dokument-deduplikering
Linje-deduplikering er en proces hvor gentagne linjer fjernes på tværs af dokumenter. Dette er især anvendeligt på web-data, hvor f.eks. cookie notifikationer og menuer gentages på tværs af mange sider. Denne type af deduplikering implementeres effektivt vha. et såkaldt Bloom filter. Visse typer af datasæt kan med fordel fritages for linje-deduplikering. F.eks. vil der i juridiske dokumenter ofte indgå en række standard formuleringer og deduplikering af disse kan ødelægge dokumenternes betydningsindhold.
I dokument-deduplikering sammenlignes alle dokumenter på tværs af det rensede dokumentkorpus og dokumenter der indholdsmæssigt er tilpas tæt på hinanden grupperes i en klynge. Fra hver klynge udtrækkes ét enkelt dokument. På den måde undgås at visse dokumenter bliver overrepræsenteret i det endelige datasæt.

## PERSONHENFØRBAR INFORMATION
Når en model trænes på data, som indeholder personhenførbar information, medfører det en risiko for at modellen reproducerer denne information under kørsler. Så vidt det er muligt detekteres disse kategorier og erstattes med generiske erstatninger af samme type. Eksempler på personhenførbar information kunne være: Navne, E-mail, Telefonnumre, CPR-numre. 
En udfordring er at hverken menneskelig eller maskinel fjernelse af personhenførbar information er 100% nøjagtigt, så datasæt uden disse er at foretrække.

## TOKENIZATION RASMUS
Tokenization er en vigtig proces i forbindelse med pretraining af sprogmodeller som f.eks. BERT, GPT og RoBERTa. Formålet med tokenization er at konvertere rå tekst til en sekvens af heltal, eller tokens, som sprogmodellen kan arbejde med.
Tokenizers er i disse dage også modeller som er trænet på tekstdata, men dog meget anderledes end store sprogmodeller. Efter træning kan en tokenizer bruges til opslag mellem sætninger og sekvenser af tokens.
Valget af tokenization-metode kan have betydning for modellens evne til at forstå sproget. Metoder som WordPiece og SentencePiece, der opdeler ord i subtokens, har vist sig at være effektive, da de kan håndtere ukendte ord og reducere størrelsen af vokabularet.
Efter tokenization vil teksten være repræsenteret som en sekvens af heltal, som kan fodres ind i sprogmodellen under træning. Modellen trænes til at kunne at forudsige næste token baseret på de foregående.
Når vi videretræner en eksisterende sprogmodel på et nyt sprog, er det nødvendigt at bruge den samme tokenizer, som blev brugt under den første træning af modellen. Dette skyldes, at modellens vægte er tilpasset de specifikke tokens som er indeholdt i denne tokenizer.
Hvis vi bruger en anden tokenizer under videretræning, vil der være et mismatch mellem de tokens som modellen forventer, og de tokens den faktisk får som input. Dette kan føre til dårligere performance eller endda forhindre modellen i at konvergere under træning.
Det er dog værd at undersøge, om det kan være fordelagtigt at udvide den eksisterende tokenizer, især hvis den model vi baserer videretræningen på ikke har en tokenizer som er særligt god til dansk. Dette er tilfældet for Mistral, men ikke i samme grad LLaMa 3.

## Løbende forbedringer
