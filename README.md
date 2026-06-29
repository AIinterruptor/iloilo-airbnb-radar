# Iloilo Airbnb Radar

Competitor pricing dashboard for short-term rentals near Festive Walk / SMDC Style Residences in Iloilo City.

## Live Dashboard

**[View Dashboard](https://aiinterruptor.github.io/iloilo-airbnb-radar/)**

## Data Source

- Booking.com structured API (via Claude Code MCP integration)
- Daily refresh via scheduled Claude Code routine
- 3km radius around Iloilo Business Park / Festive Walk

## Properties Tracked

| Tier | Examples |
|---|---|
| Direct Competitors | SMDC Style Residences units, Megaworld/Festive Walk condos |
| Premium | Seda Atria, Belmont Hotel |
| Midrange | Injap Tower, Hop Inn, Hotel Del Rio |
| Budget | One Lourdes Dormitel, Pallet Homes |

## Stack

- **Scraper**: Python + Booking.com MCP
- **Dashboard**: Static HTML + Chart.js (GitHub Pages)
- **Automation**: Claude Code daily routine → GitHub Actions
