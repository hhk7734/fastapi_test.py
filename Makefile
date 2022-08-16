remove_local:
	git remote update --prune
	git checkout origin/dev
	git for-each-ref --format '%(refname:short)' refs/heads | xargs git branch -D