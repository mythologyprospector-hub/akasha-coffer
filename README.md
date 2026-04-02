# akasha-coffer

## Engine Role

Akasha Coffer is the treasury and resource-tracking engine of the Akasha constellation.

## Why it exists

This repo exists so Akasha can track support, contributions, expenses, reserves, and resource allocation in a disciplined and transparent way.

It is not a custody wallet and it does not directly control funds on-chain. It is a canonical local ledger and playground for financial truth, allocation planning, and future integration.

## Inputs

Main inputs include:

- support events
- donations
- gig income
- manual ledger entries
- operational expenses
- allocation decisions
- configuration for public support channels

## Memory / Registry

This repo maintains:

- income ledger
- expense ledger
- reserve ledger
- coffer configuration
- future allocation history

## Relation Model

The relation model is treasury-oriented:

support source
→ income entry
→ allocation bucket
→ reserve / operations / growth / play

and

expense source
→ expense entry
→ budget bucket
→ ledger update

## Evaluator

This repo evaluates:

- balance state
- bucket distribution
- reserve sufficiency
- income vs expense flow
- simple treasury health

## Outputs

This repo produces:

- coffer status
- ledger summaries
- allocation views
- treasury snapshots
- a simple local playground page

## Position in Constellation

Akasha Coffer is the metabolic and treasury organ of the Akasha constellation.

It sits downstream from work, support, and contribution channels, and upstream from future decisions about APIs, storage, infrastructure, and experimental spending.

## Next Steps

Immediate next steps:

- add CLI commands for income, expense, and allocation
- add JSON export for dashboards
- add optional wallet lookup helpers later
- integrate with akasha-giginator expected-value flow
- add support channel snapshot rendering
