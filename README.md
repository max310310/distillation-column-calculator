# Distillation Column Calculator (McCabe-Thiele, ethanol-water)

A Python program that estimates how many trays a distillation column needs to separate a weak ethanol-water mixture into strong ethanol (top product) and almost pure water (bottom), and draws the McCabe-Thiele diagram.

I built this to teach myself a core chemical engineering method as a first step towards studying Chemical Engineering.

## What it does

- Takes the product purity, feed strength and leftover (bottoms) strength as inputs
- Finds the minimum reflux ratio
- Counts the number of trays and the feed tray at a chosen reflux ratio
- Plots the McCabe-Thiele diagram (equilibrium curve, operating lines and the stage staircase)
- Plots trays needed against reflux ratio to show the trade-off between column height and energy use

## Example result

Inputs: product 85% ethanol, feed 30%, leftover 2%, reflux = 1.5 x minimum.

- Minimum reflux ratio: about 2.0
- Trays needed: 22 (feed at tray 20, counting the bottom heater as one stage)

![McCabe-Thiele diagram](mccabe_thiele_diagram.png)
![Trays vs reflux](trays_vs_reflux.png)

## How to run

1. Open [Google Colab](https://colab.research.google.com) and create a new notebook
2. Paste the contents of `distillation_mccabe_thiele.py` into a cell
3. Press Shift + Enter

It needs numpy, scipy and matplotlib (all already installed in Colab).

## Assumptions

- 1 atm (101.3 kPa) pressure
- Constant molar overflow
- Feed is a saturated liquid
- Ideal stages (no tray efficiency)
- Product purity must stay below the ethanol-water azeotrope (about 89 mol%)

## Data source

The ethanol-water equilibrium data (mole fractions, 101.3 kPa) comes from:

Perry, R. H. and Green, D. W. (eds.), *Perry's Chemical Engineers' Handbook*, McGraw-Hill, Section 13 (Distillation), Table 13-1. [EDITION AND YEAR]

I did not have the book itself, so I checked the values against copies of the same table reproduced in other course materials.

## How I built this

I have some coding experience from my Business and Fintech diploma, but distillation and the McCabe-Thiele method were completely new to me. I used an AI assistant (Claude) to explain the chemistry and guide me step by step. I built the first versions in small pieces in Google Colab, ran each one, and changed the numbers myself to see what happened. The final version with both operating lines was written with the assistant's help, and I am still working through the parts I find hard.

## What I learned

- I first thought the graph showed things changing over time. It doesn't. Each dot is a separate measurement: a liquid with this much ethanol gives steam with that much ethanol.
- I also thought each row of the table was one boil. It is really a lookup table. Each round takes the steam from the last round and uses it as the next liquid.
- I changed the starting strength and the target to see what happens. Starting at 0.0006 and aiming for 0.89 took 20 rounds. The closer the target got to about 0.89, the more rounds it needed, because the steps get tiny near that point (the azeotrope).
- Reflux means sending some of the strong liquid back down the tower. More reflux means fewer trays but more energy, which is a trade-off.
- I am still getting my head around the operating lines on the diagram, especially the bottom one.

## Possible improvements

- Replace the data table with an activity-coefficient model (e.g. NRTL)
- Add other feed conditions (q not equal to 1)
- Add tray efficiency and an economic (cost) comparison
