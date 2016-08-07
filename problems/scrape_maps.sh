git pull origin master -f
python3 scrape_maps.py
(for x in 0*txt; do sha224sum $x; done) > _problem_hashes
python3 jsonify_problem_hashes.py > _problem_hashes
git add .
git commit -am '[Automated]: add maps and rehash'
git push origin master
