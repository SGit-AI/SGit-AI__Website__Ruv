| agent | action | resource | Ruflo default (legacy) | with ABP (enforce) |
|---|---|---|---|---|
| coder | file.write | src/** | allowed (legacy-default-allow) | allowed (allowed-by:abp:coder:write.file.project) |
| coder | test.run |  | allowed (legacy-default-allow) | allowed (allowed-by:abp:coder:execute.process.self) |
| coder | repo.commit |  | allowed (legacy-default-allow) | allowed (allowed-by:abp:coder:write.repository.project) |
| coder | repo.push | origin/feature | allowed (legacy-default-allow) | approval_required (approval-required-by:abp:coder:write.repository.tenant) |
| coder | network.fetch | registry.npmjs.org | allowed (legacy-default-allow) | allowed (allowed-by:abp:coder:send.endpoint.allowed) |
| coder | network.fetch.world | pastebin.example | allowed (legacy-default-allow) | denied (denied-by:abp:coder:send.endpoint.world) |
| coder | email.send | gmail | allowed (legacy-default-allow) | denied (denied-by:abp:coder:send.message.world) |
| tester | file.write | src/** | allowed (legacy-default-allow) | denied (denied-by:abp:tester:write.file.project) |
| researcher | credential.read | ~/.aws/credentials | allowed (legacy-default-allow) | denied (denied-by:abp:researcher:read.credential.host) |
| queen-strategic | model.call |  | allowed (legacy-default-allow) | allowed (allowed-by:abp:queen-strategic:write.budget.tenant) |
| documenter | deploy |  | allowed (legacy-default-allow) | approval_required (approval-required-by:abp:documenter:create.record.world) |

ABP gaps: 0
Ledger: legacy {"valid":true,"length":11} · abp {"valid":true,"length":11}