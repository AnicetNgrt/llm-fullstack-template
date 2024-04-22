# Components

## Guide

Components not made from any other (or merely wrappers) are put in `/primitives`

Components made of others but not intended for final use are put in `/constructive`

Components intended for final use with few configuration are put in `/applicative`

If in doubt, favor `/primitives` over `/constructive` and the later over `/applicative`.