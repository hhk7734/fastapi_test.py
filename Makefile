.PHONY: remove_local
remove_local:
	git remote update --prune
	git checkout origin/main
	git for-each-ref --format '%(refname:short)' refs/heads | xargs git branch -D

.PHONY: uvicorn
uvicorn:
	poetry run uvicorn app.test.main:app --host 0.0.0.0 --port 8000 --no-access-log --no-use-colors --reload 2>&1 \
		| jq -R -r '. as $$line | try fromjson catch $$line'