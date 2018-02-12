def full_grid_representation(grid_points):
    n = np.ceil(np.sqrt(grid_points))
    x = np.linspace(0, 1, n)
    y = np.linspace(0, 1, n)
    xx, yy = np.meshgrid(x, y)
    interp = interpolate.LinearNDInterpolator(zip(xx.flat, yy.flat), f(xx, yy).flat)

    fig = plt.figure()
    ax = fig.gca(projection='3d')
    surf = ax.plot_surface(X, Y, interp(X, Y), cmap=cm.coolwarm, linewidth=0, antialiased=False, alpha=0.5)
    ax.set_xlabel('$x_0$'); ax.set_ylabel('$x_1$');
    plt.show()
    
    print "number of grid points:  {}".format(len(xx.flat))
    #print "length of alpha vector: {}".format(len(alpha))
    print "u({0}, {1}) = {output}".format(*P, output=interp(P)[0])
    print "f({0}, {1}) = {output}".format(*P, output=f(*P))
    
    plt.plot(xx, yy, ".k")
    plt.show()