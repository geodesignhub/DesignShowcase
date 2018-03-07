# Geodesignhub Design Showcase
This plugin uses the [Geodesignhub API](https://www.geodesignhub.com/api) to download information about a design and analyze it to produce a showcase that shows important information about the design. 

### Adding your project
This plugin can be added to your project in the Administration interface or at the time of Geodesignhub project creation. 


### Motivation
A Design synthesis in Geodesignhub is a combination of different ideas that are often negotiated. Negotiations happen very fast and it is important to have deeper sense of the design and it's components and key themes which are sometimes lost in the fast paced process. Comparisons can be made in a few different ways as is shown in the schematic below. 

![screenshot](https://i.imgur.com/49niysd.jpg)
Source: [Prof. Ana Clara Moura](http://geoproea.arq.ufmg.br/equipe/prof-ana-clara-mourao-moura) of the Federal University of Minas Gerais, Brazil. 

### Details
This plugin provides visualization for any design in Geodesignhub as a one-click integration, we use the API to download all the diagrams and then Natural Lanugage toolkit and SK-Learn feature extraction to process the diagram titles and produce the visualizations. 

#### Timeline Visulationization

![screenshot3](https://i.imgur.com/sl4nQMB.png)

#### Design Components

![screenshot4](https://i.imgur.com/iMcNldq.png)

#### Taxonomy / Semiotic analysis 
We perform Natural lanugage processing and analysis on the names of diagrams and form a similiarity index to then show a graph of the different connections. 
![screenshot](https://i.imgur.com/jRBp3nR.png)

#### Conceptual / Ideology analysis
The software uses Python Natural language processing to build a world cloud of the different ideas for a place. 
![screenshot2](https://i.imgur.com/9oOQaTc.png)

#### Topological comparisons 
To be implemented

#### Geographical Comparison 
To be implemented. Geodesignhub provides a very good geographical comparison tools. 