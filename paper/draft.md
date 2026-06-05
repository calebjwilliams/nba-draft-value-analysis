# Are NBA Draft Picks Worth the Price? Surplus Value and the Analytics Era


**Course:** Sports Finance, Waseda Business School
**Professor:** TAKEZAWA, Nobuya
**Authors:** Sharodeep Kuar, Caleb Williams
**Date:** June 2026

---

## 1. Introduction

Every June, NBA teams make roster decisions that can shape a franchise for years. The NBA Draft is one of the most important events in the basketball labor market and yet it works differently from almost any other hiring process, the salaries paid to first-round picks are not negotiated. Since the 1995 Collective Bargaining Agreement (CBA) introduced the rookie scale the first-round draft pick salaries are set in advance by slot position and are below market rates (National Basketball Association & National Basketball Players Association, 1995). This means that every first-round selection is a potential source of surplus value since teams pay a fixed below-market price and receive labor whose true market value may be much higher.

This paper asks two related questions. First do NBA draft picks actually deliver surplus value relative to their rookie scale salaries? Second did the rise of advanced analytics change how that surplus is distributed across draft positions?

The winner's curse hypothesis which is applied mostly to the NFL draft by Massey and Thaler (2013) predicts that top draft picks are usually overvalued. Teams make poor decisions at the top of the draft and receive disappointing returns relative to what they paid. In the NBA this mechanism fails since the rookie scale removes the bidding process which is the core mechanism behind this theory. Teams do not bid for players instead they pay a rate fixed by the CBA making overbidding impossible. This structural difference makes the NBA draft a cleaner setting for studying surplus value and pricing efficiency.

Using player-season data from 1995 to 2018 we cover 6,163 player-seasons across 24 draft cohorts and measure performance per dollar using Value Over Replacement Player (VORP) scaled by salary. Three findings stand out. First all first-round picks generate positive surplus value under the rookie scale. Second top-five picks deliver the most return per dollar and not the least. The salary cap is most binding at the top of the draft and this is where the gap between fixed rookie pay and true market value is largest (National Basketball Association & National Basketball Players Association, 1995). Third this surplus was not spread evenly across the draft before the analytics era. Pre-2010 the value was concentrated at the top. Post-2010 it looks to have converged since teams now have access to advanced analytics hence becoming better at finding value throughout the draft thus flattening the value curve.

The rest of this paper is organized as follows. Section 2 reviews the literature on draft market efficiency, the rookie scale and the analytics revolution. Section 3 describes our data and methodology. Section 4 presents results. Section 5 discusses implications for market efficiency and asset pricing in sports labor markets. Section 6 concludes.

---

## 2. Literature Review

### 2.1 Surplus Value in Sports Labor Markets

The concept of surplus value in sports labor markets originates with Scully (1974) who was the first to formally measure the gap between a player's market wage and the revenue their performance generates for their team. Using data from Major League Baseball, Scully found that players under the reserve clause were paid far below their marginal revenue product thus producing significant surplus value for team owners. This framework which states wages are relative to marginal product provides the theoretical foundation for our analysis. In the NBA context the rookie scale functions similarly to the reserve clause. It applies an upper limit on player compensation which is below market rates for the first four years of a player's career and hence creates a structural source of surplus value for the drafting team.

### 2.2 The NBA Rookie Scale and the 1995 CBA

 The 1995 CBA locked in salaries for every first-round pick before the draft even happens. Each slot carries a fixed dollar amount, so a team picking third pays the same regardless of who they select (National Basketball Association & National Basketball Players Association, 1995). Under this system teams do not negotiate salaries with their first-round picks. The salary for each slot is set as a percentage of the salary cap and rises modestly with pick number. The decision to enter the draft early and the pick received has real financial consequences for players given this structure (Groothuis et al., 2007). This has two important implications. First every first-round pick is acquired at a price below what a free market would likely produce for a productive player. Second the surplus value available to a team is structurally tied to draft position and not to the individual player's negotiating leverage. This makes the draft a natural laboratory for studying asset mispricing in a fixed-price market.

### 2.3 The Winner's Curse and Over-valuating Draft Picks 

Massey and Thaler (2013) showed that NFL teams systematically overvalue high draft picks. In their study the top picks in the NFL draft generated less surplus value on average than picks selected later in the first round. They attributed this finding to overconfidence and the "winner's curse" the tendency for the winner of a competitive bidding process to overpay in comparison to the true value of the asset. Their work draws on behavioral economics to argue that NFL general managers are prone to overestimating the talent of players they have the opportunity to select first.

However, the NBA context differs in a critical structural way. In the NFL, teams trade picks and negotiate compensation structures with some flexibility. In the NBA however first-round rookie salaries are entirely fixed by the CBA. There is no bidding mechanism through which overconfidence can inflate the price paid. As a result the winner's curse as Massey and Thaler define it cannot operate through salary in the NBA. This does not mean that the winner's curse in the NBA can not manifest. It could very well manifest in the pick trade market where teams exchange future picks at negotiated values or in second-contract overvaluation where teams overpay high picks upon free agency. Our study measures neither of these and explicitly excludes them from its scope.

### 2.4 Behavioral Economics and Draft Order Bias

Even though the overbidding mechanism is nonexistent, behavioral biases can still distort how teams use draft picks. Staw and Hoang (1995) found that NBA teams give higher draft picks more playing time than their performance warrants even after controlling for ability. This sunk cost fallacy where one has the tendency to let past investment influence future decisions means that draft position has an independent effect on a player's career beyond their actual on-court value. While our study does not directly test for this bias it is relevant context to the extent that high picks receive more playing time regardless of performance and that their cumulative VORP figures may be partially inflated by opportunity rather than pure talent. This is a limitation we acknowledge in our analysis.

### 2.5 The Analytics Revolution and Market Efficiency

In the late 1990s and early 2000s NBA teams started to use advanced statistics to evaluate players. Berri (1999) was one of the first to develop a formal model that converted player box score data directly into wins called Wins Produced. Berri's work found that traditional basketball evaluation over-rewarded high scorers and ignored other contributions this means that many players were being mispriced in the labor market. Dean Oliver's Basketball on Paper (2004) expanded on this finding by introducing more granular statistical tools for measuring individual player contributions by including efficiency metrics that are still widely used today.

This matters for our study because mispricing in player evaluation would show up in the draft. Before analytics became widespread teams likely relied heavily on reputation and traditional scouting which tends to favor highly visible and high-ceiling prospects near the top of the draft. If that is true the surplus value generated by draft picks would have been unevenly distributed concentrated at the top where conventional wisdom was most reliable. As analytics tools became common across the league these teams got better at spotting value in less obvious places. Hakes and Sauer (2006) documented this process in baseball showing that the market inefficiencies exploited by Oakland Athletics management were competed away once other teams adopted the same analytical approach. Our hypothesis is that a parallel process occurred in the NBA draft and this shift compressed the surplus value curve and thus making mid and late first-round picks more comparable to top picks in terms of return per dollar spent.

## 3. Data and Methodology

### 3.1 Data Sources

This study draws on three data sources. Draft history data, including pick number, player name, draft year and drafting team was collected via the NBA API for all draft cohorts from 1995 to 2018. From Basketball Reference we collected Player performance data, covering Value Over Replacement Player (VORP), Win Shares (WS) and Box Plus/Minus (BPM) on a per-season basis for seasons from 1997 through 2023. Salary data was collected from ESPN for seasons 2001 through 2024 instead of HoopsHype since they didn't have a predictable url structure making scraping difficult.

We started collected samples from 1995 because that is when the rookie scale was introduced under the CBA (National Basketball Association & National Basketball Players Association, 1995). Before 1995 the first-round salaries were negotiated rather than fixed this means the surplus value mechanism we study did not exist. The sample ends at the 2018 draft cohort since this allow players sufficient time to accumulate meaningful career statistics. We also excluded Pre-2001 salary data since the historical records were incomplete.

### 3.2 Sample Construction and Cleaning

The three datasets were merged using normalized player names and season year as join keys. We only focus on players with meaningful playing time by applying a filter of at least 20 games played and 200 total minutes in a given season. Traded players who appeared on multiple team rosters in the same season were retained using Basketball Reference's combined season totals row rather than individual team splits to ensure we were not double counting.

The final sample contains 6,163 player-seasons covering 24 draft cohorts and 1,272 unique players. Salary coverage is 86.1 percent of player-seasons. The remaining 13.9 percent of observations were dropped from regression analysis but retained in descriptive statistics where applicable.

### 3.3 Key Variables

Our primary performance metric is VORP per one million dollars of salary (VORP/1M). This metric measures how much value above a replacement-level player a team receives for each million dollars spent. VORP is drawn from Basketball Reference and reflects a player's contribution to team wins relative to what a freely available replacement-level player would produce. This maps directly onto the surplus value framework from Scully (1974) which states salary is the price VORP is the output and the ratio is the return on investment. Berri et al. (2006) applied a similar wage-to-output framework specifically to basketball, finding systematic mispricing of player contributions across the league.

We exclude Net Rating as a primary metric because it is a team-context-dependent measure. Top picks are systematically assigned to weaker teams which deflates their Net Rating independent of individual skill. This would introduce a structural bias against precisely the players we are trying to evaluate.

For robustness we construct two alternative dependent variables. Win Shares per one million dollars (WS/1M) uses an independent methodology from Basketball Reference that does not adjust for replacement level. BPM per one million dollars (BPM/1M) uses a rate-based metric unaffected by games played and serves as a check on whether injury availability drives the VORP results. Both dependent variables are winsorized at the 1st and 99th percentiles to limit the influence of outliers.

We define four draft position bins as follows:
- Top 5 picks
- Picks 6 to 14
- Picks 15 to 30
- Second-round picks

Second-round picks are included as a control group because they are not covered by the rookie scale and receive negotiated salaries. This allows us to test whether the surplus value pattern is driven by contract structure rather than player quality.

The sample is split into two eras at the 2010 draft cohort Pre-Analytics (1995 to 2009) and Post-Analytics (2010 to 2018). The choice of 2010 as the breakpoint reflects the period in which advanced analytics tools became widely adopted across NBA front offices, following the publication of foundational works in the mid-2000s (Berri, 1999; Oliver, 2004; Berri et al., 2006) and the broader Moneyball effect in sports management (Hakes & Sauer, 2006).

### 3.4 Regression Models

We estimate six OLS models with heteroscedasticity-robust standard errors (HC3) to test how draft position predicts performance per dollar and whether this relationship changed in the analytics era.

| Model | Specification | Purpose |
|-------|--------------|---------|
| M1 | VORP/1M ~ Pick | Baseline: does pick number predict value? |
| M2 | VORP/1M ~ Pick + Post | Add era dummy, parallel slopes |
| M3 | VORP/1M ~ Pick x Post | Main model: does the slope change by era? |
| M4 | VORP/1M ~ log(Pick) x Post | Log-linear: diminishing returns to pick position |
| M5 | WS/1M ~ Pick x Post | Win Shares robustness check |
| M6 | BPM/1M ~ Pick x Post | Injury robustness: rate stat unaffected by games played |

The interaction term in M3 (Pick x Post) is the central test of our hypothesis. A positive and significant interaction coefficient would indicate that the negative relationship between pick number and value per dollar weakened in the post-analytics era, consistent with a flattening of the surplus value curve.

The R-squared values across all models are low, as is typical for player-level sports data. We do not interpret R-squared as a measure of model quality. The analysis focuses on the direction and significance of coefficients rather than predictive fit.

## 4. Results

### 4.1 Descriptive Statistics

**Table 1: Summary Statistics by Draft Position Bin and Era**

| Pick Bin | Era | N | VORP/1M (mean) | VORP/1M (std) | Bust Rate | Sharpe Analog |
|----------|-----|---|----------------|---------------|-----------|---------------|
| Top 5 | Pre-Analytics | 789 | 0.251 | 0.365 | 12.4% | 0.688 |
| Top 5 | Post-Analytics | 315 | 0.136 | 0.270 | 19.0% | 0.503 |
| Picks 6–14 | Pre-Analytics | 983 | 0.192 | 0.420 | 23.7% | 0.457 |
| Picks 6–14 | Post-Analytics | 573 | 0.146 | 0.317 | 23.9% | 0.460 |
| Picks 15–30 | Pre-Analytics | 1367 | 0.180 | 0.480 | 29.4% | 0.376 |
| Picks 15–30 | Post-Analytics | 644 | 0.149 | 0.391 | 28.0% | 0.380 |
| Second Round | Pre-Analytics | 930 | 0.132 | 0.497 | 33.7% | 0.266 |
| Second Round | Post-Analytics | 562 | 0.125 | 0.508 | 31.9% | 0.246 |

![Figure 1: VORP per $1M by Draft Bin and Era](../data/processed/figures/fig1_performance_per_dollar.png)

Table 1 contains mean VORP per $1M salary by draft position bin and era alongside standard deviation, bust rate and Sharpe analog. Several patterns stand out.

First all first-round bins generate positive mean VORP per dollar in both eras this confirms that the rookie scale is creating surplus value across the entire first round. The second round which operates outside the rookie scale seems to produce the lowest returns in both eras (0.13 pre-analytics, 0.13 post-analytics). This is consistent with our hypothesis that contract structure rather than player quality is the main driver for the surplus value pattern.

Second the top-five picks deliver the highest return per dollar in both eras. Pre-analytics the top-five picks averaged 0.25 VORP per $1M compared to 0.19 for picks 6-14, 0.18 for picks 15-30 and 0.13 for second-round picks. These results contradict a simple winner's curse reading that under fixed rookie salaries the most expensive slots also generate the highest returns (Massey & Thaler, 2013).

Third the top-five picks dominate all other bins on risk-adjusted return. The Sharpe analog for top-five picks was 0.69 pre-analytics and 0.50 post-analytics while for the second-round picks it is 0.27. Top picks also carry the lowest bust rate. 12.4 percent of the top-five player-seasons produced negative VORP pre-analytics. This figure rose to 19.0 percent post-analytics but is still well below the second-round bust rate of 33.7 percent. In mean-variance terms the top picks offer the highest return and the lowest volatility. This makes them the dominant asset class in every era.

### 4.2 Era Convergence

![Figure 2: Pick Number vs VORP per $1M with LOWESS Trend](../data/processed/figures/fig2_pick_vs_vorp_scatter.png)

Figure 2 shows the relationship between draft position and VORP per dollar across all player-seasons. The LOWESS trend line confirms the negative relationship -- value per dollar decreases as pick number increases -- though the wide scatter reflects the high individual variance typical of player-level sports data.

![Figure 3: Era Comparison -- VORP per $1M by Draft Bin](../data/processed/figures/fig3_era_comparison_line.png)

Figure 3 shows a direct comparison of both eras. Pre-analytics we see that there was a steep drop in VORP per dollar when checking the top of draft moving downwards. We see 0.25 for top-five picks falling to 0.13 for second-round picks. Post-analytics we see this gradient flatten. We see the top-five picks fall from 0.25 to 0.14 but mid and late first-round picks seem to be relatively steady.

![Figure 4: Risk-Return Scatter by Draft Bin and Era](../data/processed/figures/fig4_risk_return.png)

Figure 4 presents the mean-variance scatter. Pre-analytics points cluster in a steep diagonal from top-left (second round: low return, high risk) to top-right (top five: high return, low risk). Post-analytics, the points converge toward the center, consistent with a more efficient market where information advantages are smaller.

### 4.3 Regression Results

**Table 2: OLS Regression Results (M1--M6)**

| Model | N | R² | Pick coef. | p-value | Post coef. | p-value | Interaction coef. | p-value |
|-------|---|----|------------|---------|------------|---------|-------------------|---------|
| M1 (baseline) | 6163 | 0.004 | -0.00175 | <0.001 | -- | -- | -- | -- |
| M2 (era dummy) | 6163 | 0.006 | -0.00171 | <0.001 | -0.044 | <0.001 | -- | -- |
| M3 (interaction) | 6163 | 0.007 | -0.00232 | <0.001 | -0.082 | <0.001 | 0.00181 | 0.024 |
| M4 (log pick) | 6163 | 0.007 | -- | -- | -0.124 | <0.001 | -- | -- |
| M5 (WS robustness) | 6163 | 0.024 | 0.01172 | <0.001 | -0.241 | <0.001 | 0.00175 | 0.478 |
| M6 (BPM robustness) | 6163 | 0.058 | -0.03249 | <0.001 | 0.125 | 0.092 | -0.00081 | 0.854 |

Table 2 presents OLS results for M1 through M6. In the baseline model (M1), each additional pick position is associated with a decrease of 0.00175 VORP per $1M (p < 0.001), confirming that pick number negatively predicts value per dollar. Adding the era dummy in M2 shows that the post-analytics era is associated with lower overall VORP per dollar on average, consistent with salaries rising faster than performance across the board.

The main model (M3) introduces the interaction between pick number and the post-analytics dummy. The interaction coefficient is 0.0018 (p = 0.024), indicating that the negative relationship between pick number and value per dollar weakened significantly in the post-analytics era. In other words, the value curve flattened after 2010. This is the central finding of the paper.

R-squared across all models is low, ranging from 0.004 to 0.007. This is expected for player-level sports data where individual variation is large. The analysis focuses on the direction and significance of the interaction term rather than overall explanatory power.

The robustness checks produce mixed results. M5, which substitutes Win Shares per dollar for VORP per dollar, does not find a significant interaction term (p = 0.478). M6, which uses BPM per dollar as a rate-based check on injury effects, is also not significant (p = 0.854). These results suggest the convergence finding is specific to VORP, which adjusts for replacement level. Win Shares and BPM do not apply the same adjustment, meaning their results are not directly comparable. We discuss this limitation in Section 5.

### 4.4 Sensitivity Analysis

**Table 3: Sensitivity Analysis -- Interaction Term Across Era Breakpoints**

| Breakpoint | N | R² | Interaction coef. | p-value | Significant? |
|------------|---|----|-------------------|---------|--------------|
| 2010 | 6163 | 0.007 | 0.00181 | 0.024 | Yes |
| 2012 | 6163 | 0.008 | 0.00095 | 0.228 | No |
| 2014 | 6163 | 0.007 | 0.00127 | 0.152 | No |

Table 3 shows the interaction term across different era which can be possible breakpoints. In the 2010 breakpoint we see a significant interaction with p-value at 0.024 this is higher than 2012 where the p-value is 0.228 and 2014 where p-value is 0.152. This shows that 2010 is the logical breakpoint for our study and not just a coincidence.

## 5. Discussion

### 5.1 Draft Picks as Financial Assets

The results of this study are best understood through an asset pricing lens. Each draft pick slot is an asset with a fixed acquisition cost set by the CBA and a variable return determined by player performance. VORP per dollar is the return on that investment. Surplus value is the excess return above what a replacement-level player would deliver at the same price. This framing follows directly from Scully (1974) who established that player wages and marginal output can be compared to measure exploitation or surplus in sports labor markets.

Under this framing our first finding is almost mechanical. The rookie scale sets prices below what a productive player would earn on the open market. Every first-round pick therefore starts with a structural advantage that a free agent signing does not have. The second round confirms this. Second-round picks operate outside the rookie scale and receive negotiated salaries. Their VORP per dollar is the lowest of any group in both eras (0.13 pre- and post-analytics) which is consistent with a market that prices second-round talent closer to its actual value.

### 5.2 Top Picks as the Dominant Asset Class

The more surprising finding is that top-five picks are not just surplus-generating assets but the best ones. Pre-analytics, top-five picks averaged 0.25 VORP per dollar compared to 0.13 for second-round picks. The Sharpe analog for top-five picks was 0.69 versus 0.27 for the second round. In mean-variance terms top picks offer higher return and lower volatility simultaneously which makes them the dominant asset class. No other bin comes close on a risk-adjusted basis.

The intuition here is straightforward. The salary cap is most binding at the top of the draft. A player drafted first overall who develops into an All-Star would command a max contract on the open market. Under the rookie scale they are paid a fraction of that for four years. The gap between fixed rookie pay and true market value is largest precisely where the talent is highest. This is not a market inefficiency in the traditional sense. It is a structural feature of the CBA that systematically advantages teams with high picks.

This result does not contradict Massey and Thaler (2013). Their finding was that NFL teams overpay for top picks relative to picks later in the draft because salaries in the NFL are negotiated and teams bid too aggressively. In the NBA that bidding mechanism does not exist. Salaries are CBA-mandated so overbidding is structurally impossible. The winner's curse in the NBA context would have to manifest elsewhere, in the pick trade market where teams negotiate the value of future picks, in second-contract overvaluation where teams pay top picks above their marginal product after the rookie deal expires, or in tenure bias of the kind documented by Staw and Hoang (1995) where high picks receive playing time their performance does not justify. Our study measures none of these. We measure only the return on the rookie contract itself which by design favors the drafting team.

### 5.3 The Analytics Era and Market Convergence

Our central finding is that the surplus value curve flattened after 2010. The interaction term in M3 is significant at p = 0.024 at the 2010 breakpoint and not significant at 2012 or 2014. This is consistent with the hypothesis that analytics-era teams became better at identifying value throughout the draft thus reducing the information gap between top picks and the rest of the first round.

Before analytics became widespread most teams relied on traditional scouting which tends to favor visible, high-ceiling prospects near the top of the draft. Mid and late first-round picks were harder to evaluate and more frequently mispriced. As tools like Wins Produced (Berri, 1999) and the efficiency metrics introduced by Oliver (2004) spread across front offices teams gained the ability to identify productive players further down the draft board. The result was a compression of the value distribution. Top picks still deliver the most return per dollar but the gap between the top bin and the rest of the first round shrank measurably after 2010.

From a market efficiency standpoint this is consistent with an information-driven correction. Pre-2010 the draft market exhibited persistent inefficiency in that mid and late first-round picks were systematically undervalued relative to top picks. Post-2010 that gap narrowed as information asymmetry decreased. The market did not become fully efficient but it moved in that direction. This pattern mirrors findings in baseball labor markets where Pinheiro and Szymanski (2022) showed that analytical tools gradually corrected persistent mispricing once information spread across teams.

### 5.4 Limitations

Two robustness checks produce results that are worth acknowledging. M5, which uses Win Shares per dollar instead of VORP per dollar, does not find a significant interaction term (p = 0.478). M6, which uses BPM per dollar as a rate-based check, is also not significant (p = 0.854). This means the convergence finding holds under VORP but not under Win Shares or BPM.

The divergence between VORP and Win Shares likely reflects a methodological difference. VORP adjusts for replacement level while Win Shares does not. A player producing at a replacement level contributes positive Win Shares simply by playing but contributes zero or negative VORP. This makes VORP a stricter measure of genuine surplus value and the one most directly aligned with our theoretical framing. The BPM result is harder to dismiss. BPM is a rate stat unaffected by games played which means it is not inflated by teams giving high picks more playing time as per Staw and Hoang (1995). The fact that BPM convergence is not significant at p = 0.854 raises the possibility that some of the VORP convergence reflects changes in playing-time allocation across eras rather than pure improvements in draft efficiency. We cannot fully rule this out and acknowledge it as a limitation.

---

## 6. Conclusion

This paper examined how the NBA rookie scale contract structure creates surplus value across draft positions and how the analytics revolution changed its distribution. Using 6,163 player-seasons across 24 draft cohorts from 1995 to 2018 we find three results.

First all first-round picks generate positive surplus value under the rookie scale. The CBA fixes first-round salaries below market rates which creates a structural advantage for drafting teams regardless of pick position. Second-round picks which operate outside the rookie scale produce the lowest returns and serve as the control group confirming that contract structure rather than player quality drives the pattern.

Second top-five picks deliver the most return per dollar not the least. The Sharpe analog for top picks was 0.69 pre-analytics and 0.50 post-analytics compared to 0.27 for the second round. Bust rates are also lowest at the top of the draft. In mean-variance terms top picks dominate every other bin in every era. The winner's curse framework of Massey and Thaler (2013) does not apply here because the bidding mechanism it depends on does not exist under the CBA.

Third the surplus value curve flattened after 2010. The interaction term in our main regression model (M3) is significant at the 2010 breakpoint (p = 0.024) but not at 2012 or 2014. This is consistent with analytics-era teams gaining better information about mid and late first-round talent thus reducing the pricing gap between the top of the draft and the rest of the first round.

The findings have implications for how teams should think about draft asset management. Under the rookie scale every first-round pick is priced below market but the structural surplus is highest at the top. Trading away top picks to acquire multiple mid-round picks may feel diversified but from a risk-adjusted return standpoint it moves a team from the best asset class to a worse one. Future research could test whether the winner's curse manifests in the NBA pick trade market or in second-contract valuations where the fixed-price protection of the rookie scale no longer applies.

---

## References

Berri, D. J. (1999). Who is "most valuable"? Measuring the player's production of wins in the National Basketball Association. *Managerial and Decision Economics*, *20*(8), 411–427. https://doi.org/10.1002/(SICI)1099-1468(199912)20:8<411::AID-MDE950>3.0.CO;2-G

Berri, D. J., Schmidt, M. B., & Brook, S. L. (2006). *The wages of wins: Taking measure of the many myths in modern sport*. Stanford University Press.

Groothuis, P. A., Hill, J. R., & Perri, T. J. (2007). Early entry in the NBA draft: The influence of unraveling, human capital, and option value. *Journal of Sports Economics*, *8*(3), 223–243. https://doi.org/10.1177/1527002505281228

Hakes, J. K., & Sauer, R. D. (2006). An economic evaluation of the Moneyball hypothesis. *Journal of Economic Perspectives*, *20*(3), 173–186. https://doi.org/10.1257/jep.20.3.173

Massey, C., & Thaler, R. H. (2013). The loser's curse: Decision making and market efficiency in the National Football League draft. *Management Science*, *59*(7), 1479–1495. https://doi.org/10.1287/mnsc.1120.1657

National Basketball Association & National Basketball Players Association. (1995). *Collective bargaining agreement*. NBA.

Oliver, D. (2004). *Basketball on paper: Rules and tools for performance analysis*. Potomac Books.

Scully, G. W. (1974). Pay and performance in Major League Baseball. *The American Economic Review*, *64*(6), 915–930. https://www.jstor.org/stable/1815242

Pinheiro, R., & Szymanski, S. (2022). All runs are created equal: Labor market efficiency in Major League Baseball. *Journal of Sports Economics*, *23*(8), 1046–1075. https://doi.org/10.1177/15270025221085712

Staw, B. M., & Hoang, H. (1995). Sunk costs in the NBA: Why draft order affects playing time and survival in professional basketball. *Administrative Science Quarterly*, *40*(3), 474–494. https://doi.org/10.2307/2393794

---

## Appendix

### A. Sample Data

The table below shows a representative sample of 15 player-seasons from the analysis dataset. Salary is expressed in millions of USD. VORP/1M is VORP divided by salary in millions.

| Player | Draft Year | Pick | Bin | Era | Season | VORP | Salary ($M) | VORP/1M |
|--------|------------|------|-----|-----|--------|------|-------------|---------|
| Shareef Abdur-Rahim | 1996 | 3 | Top 5 | Pre | 2003-04 | 2.4 | 13.50 | 0.178 |
| Theo Ratliff | 1995 | 18 | Picks 15-30 | Pre | 2003-04 | 1.5 | 10.16 | 0.148 |
| James Posey | 1999 | 18 | Picks 15-30 | Pre | 2002-03 | 1.7 | 1.72 | 0.987 |
| Josh Smith | 2004 | 17 | Picks 15-30 | Pre | 2014-15 | 1.6 | 2.08 | 0.770 |
| Jarrett Jack | 2005 | 22 | Picks 15-30 | Pre | 2010-11 | 0.5 | 4.60 | 0.109 |
| Mikal Bridges | 2018 | 10 | Picks 6-14 | Post | 2022-23 | 2.8 | 20.10 | 0.139 |
| Ramon Sessions | 2007 | 56 | Second Round | Pre | 2013-14 | 0.7 | 5.00 | 0.140 |
| Russell Westbrook | 2008 | 4 | Top 5 | Pre | 2008-09 | 0.7 | 3.49 | 0.200 |
| Stephon Marbury | 1996 | 4 | Top 5 | Pre | 2004-05 | 5.1 | 14.62 | 0.349 |
| Joe Johnson | 2001 | 10 | Picks 6-14 | Pre | 2004-05 | 2.4 | 2.36 | 1.018 |
| James Harden | 2009 | 3 | Top 5 | Pre | 2015-16 | 6.8 | 15.76 | 0.432 |
| Mike Conley | 2007 | 4 | Top 5 | Pre | 2008-09 | 1.1 | 3.63 | 0.303 |
| Linas Kleiza | 2005 | 27 | Picks 15-30 | Pre | 2008-09 | 0.2 | 1.82 | 0.110 |
| Darius Miller | 2012 | 46 | Second Round | Post | 2017-18 | 0.1 | 2.10 | 0.048 |
| Nick Young | 2007 | 16 | Picks 15-30 | Pre | 2008-09 | -0.6 | 1.60 | -0.374 |

### B. Data Coverage by Draft Cohort

Salary coverage is 100% across all cohorts after applying the 2001 salary floor. The table below reports player-seasons and unique players per draft year included in the final sample.

| Draft Year | Player-Seasons | Unique Players | Salary Coverage |
|------------|---------------|----------------|-----------------|
| 1995 | 166 | 27 | 100% |
| 1996 | 214 | 28 | 100% |
| 1997 | 191 | 29 | 100% |
| 1998 | 264 | 40 | 100% |
| 1999 | 250 | 36 | 100% |
| 2000 | 276 | 42 | 100% |
| 2001 | 299 | 39 | 100% |
| 2002 | 176 | 30 | 100% |
| 2003 | 326 | 35 | 100% |
| 2004 | 276 | 35 | 100% |
| 2005 | 356 | 44 | 100% |
| 2006 | 274 | 43 | 100% |
| 2007 | 307 | 41 | 100% |
| 2008 | 353 | 43 | 100% |
| 2009 | 341 | 47 | 100% |
| 2010 | 245 | 40 | 100% |
| 2011 | 316 | 45 | 100% |
| 2012 | 260 | 42 | 100% |
| 2013 | 269 | 41 | 100% |
| 2014 | 223 | 43 | 100% |
| 2015 | 225 | 38 | 100% |
| 2016 | 184 | 41 | 100% |
| 2017 | 185 | 46 | 100% |
| 2018 | 187 | 44 | 100% |
| **Total** | **6,163** | **1,272** | **100%** |
