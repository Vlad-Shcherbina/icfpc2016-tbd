set -x

git pull origin master -f
python3 scrape_maps.py
(for x in 0*txt; do sha224sum $x; done) > _problem_hashes
python3 jsonify_problem_hashes.py > __problem_hashes
cd ../manpages_scratch/
python3 produce_stats_of_our_problems.py  > our_problems.txt
python3 _produce_stats_of_all_problems.py > all_problems.txt
cd ../problems/
git add .
git commit -am '[Automated]: add maps and rehash'
git push origin master
