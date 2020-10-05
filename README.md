# Introduction and Motivation
[![<ORG_NAME>](https://circleci.com/github/Masamerc/fennec-alert.svg?style=svg)](<LINK>)

Airflow pipeline with Slackbot I wrote to get notifications on daily items on https://rocket-league.com/items/shop.
As you all know (\s), Rocket League is "the high-powered hybrid of arcade-style soccer and vehicular mayhem".

I am in the process of collecting rare cars in the game, but the problem is - the items changes on daily rotations, thus I have to check what's in store every day.

After a couple of months of checking the shop in the morning only to be disappointed, I decided to build a simple airflow pipeline that watches the shop and send me slack message if any of my desired items is in the shop.

<br>
<p align="center">
  <img src="beautiful_beast.png" />
</p>
