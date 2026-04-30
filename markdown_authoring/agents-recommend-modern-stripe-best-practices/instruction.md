# Recommend modern Stripe best practices

Source: [wshobson/agents#435](https://github.com/wshobson/agents/pull/435)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/payment-processing/skills/stripe-integration/SKILL.md`

## What to add / change

Hi there 👋🏻 I work at Stripe.

## Changes

- Clarify that Checkout Sessions is the recommended path for not just Hosted Checkout, but [also Elements](https://docs.stripe.com/payments/checkout-sessions-and-payment-intents-comparison). 
- Remove Card Element example. [Card Element is a legacy element, and Payment Element is the suggested replacement](https://docs.stripe.com/payments/payment-card-element-comparison).
- Remove the hard-coded `payment_method_types` param in Checkout Session creation requests. [Dynamic payment methods](https://docs.stripe.com/payments/payment-methods/dynamic-payment-methods) are recommended.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
