from .shortmute import Shortmute


def setup(bot):
    bot.add_cog(Shortmute(bot))