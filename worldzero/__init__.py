from .worldzero import WorldZero


def setup(bot):
    bot.add_cog(WorldZero(bot))
