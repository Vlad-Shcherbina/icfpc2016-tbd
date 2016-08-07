from production import cg, ioformats

from production import render

def main():
    problems = [342, 989, 1456, 2606, 3560, 3852, 3854, 3929, 4008, 4010, 4229, 4236, 4239, 4461, 4861, 5195, 5199, 5293, 5311, 5724, 5726, 5907, 5933, 5949]
    for p in problems:
        pr = '{0:05d}'.format(p)
        with open('solutions/%s-ch.txt' % pr, 'r') as s:
          sol = s.read()
          sol = ioformats.parse_solution(sol)
        img = render.render_solution(sol, 500)

        img.save('img/convexsolution%s.png' % pr)




if __name__ == '__main__':
    main()
