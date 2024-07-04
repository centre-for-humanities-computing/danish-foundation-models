---
draft: false
date: 2024-07-04
auther: jens.benner@alexandra.dk
---


# Datakilder
De data som sprogmodeller trænes på er afgørende for hvad de kan bruges til. I Danish Foundation Models er tilgangen at vi skal have sikkerhed for at vi må benytte de data vi træner på fra data ejere, samt at vi har fokus på værdiskabende use-cases. Dette gør vi blandt andet gennem samarbejdet med [Dansk Sprogmodel Konsortium](https://alexandra.dk/dansk-sprogmodel-konsortium/).

<!-- more -->
## Nuværende datakilder
Vi arbejder kontinuerligt på at indsamle data fra flere kilder. Nedenstående tabel indeholder kilder som lige nu, efter bedste overbevisning, kan anvendes til træning af en dansk sprogmodel. Mængden af data vi har nu, er ikke tilstrækkelig til at træne en dansk sprogmodel fra grunden. Størrelsen er angivet i antal tegn.


| Datasæt                   | Dato	      | Domæne	              | Licens	           | Størrelse |
| --------------------------|-------------|-----------------------|--------------------|----------|
| AI aktindsigt 	        | nutidig     | Kommunale hjemmesider   |	CC0-1.0		       | 408M      |
| Domsdatabasen	            | 1855-nu	  | Domme	                | CC0-1.0		       | 91.2M      |
| Eur-lex-sum-da            | 1993-nu     | Jura (EU)	           |  CC-BY-SA 4.0 	   | 87.8M      |
| FTSpeech	                | 2017-nu	  | Folketingets taler	    | Ikke standard 	   | 244M      |
| Scrape Hovedstaden	    | nutidig	  | Sundhed	                | CC0-1.0		       | 79.9M      |
| MeMo                      | 1870-1899	  | Skønlitteratur	     |    Offentligt Domæne  | 319M      |
| Wikipedia	                | nutidig	  | Encyklopædi	            | CC-BY-SA 4.0	   | 498M      |
| Retsinformation.dk (*)	| nutidig	  | Lovtekster	            | Ikke standard (*)  | 1.42G      |            
| Skat.dk (*)	            | nutidig	  | Skatteinformation	    | CC0-1.0		       | 354M      |
| H-Sø (*)	                | nutidig     | Retssager	         |    CC0-1.0		       | 204      |
| Hestenettet (*)	        | nutidig	  | Forum	                | CC0-1.0		       | 1.19G      |
| Folketinget (*)	        | 2009-2019	  | Debat	               |  Ikke standard 	   | 351M      |
| Europarl (*)	            | 2004-2008	  | Debat	              |   CC0-1.0		       | 312M      |
| Spontaneous Speech (*)	| 2019	      | Samtaler	            | CC0-1.0		       | 4.0M      |
| NAAT (*)	                | 1930-nu	  | Taler	                | CC0-1.0		       | 881k      |
| Dansk Litteratur (*)	    | 1700-nu	  | Litteratur	            | CC0-1.0		       | 162M      |
| Gutenberg (*)	            | 1700-nu	  | Litteratur	           |  Ikke Standard	   | 19.2M      |
| WikiBooks (*)	            | 2019-2020	  | Manualer	           |  CC0-1.0		       | 17.5M      |
| WikiSource (*)	        | 1700-nu	  | Litteratur	            | CC0-1.0		       | 15.5M      |
| Johannes V. Jensen (*)	| -	          | JVJ’s værker	        | CC-BY-SA 4.0	   | 10.7M      |
| Religiøse Tekster (*)     | -	          | Religiøse	            | CC0-1.0		       | 3.56M      |
| TV2R (*)	                | 2015-2019	  | Nyheder	              |   CC-BY 4.0		   | 64.04M      |
| Dasem Data (*)	        | nutidig	  | Andet	                | Ikke standard	   | 4.45M      |
| Botxt (*)	                | nutidig	  | Bornholmsk	         |    CC0-1.0		       | 2.01M      |
| DDT (*)	                | nutidig	  | Andet	                | CC-BY-SA 4.0	   | 546k      |
| Sønderjysk (*)	        |nutidig	  | Sønderjysk	           |  CC0-1.0		       | 140k      |

Listen vil løbende blive opdateret med flere datakilder. Data kommer bl.a. til at være fra samarbejdet med Dansk Sprogmodel Konsortium. Det skal bemærkes at nogle af datasættene kommer fra [Danish Gigaword](https://gigaword.dk/), angivet i tabellen med (*).

## Respekt for dataejere
Vi har den største respekt for dem, der ejer data. Vi forstår, hvor vigtigt det er at beskytte og respektere dataejeres ønsker om hvad deres data må bruges til. Hvis du har nogen spørgsmål vedrørende de data vi bruger, er du altid velkommen til at kontakte os. Vi er meget åbne for dialog og sætter pris på input, da det hjælper os med at forbedre vores praksis og sikre, at vi lever op til dataejeres ønsker. Din feedback er vigtig for os, og vi ser frem til at høre fra dig.
