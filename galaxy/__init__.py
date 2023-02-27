from .galaxy import Galaxy


def setup(bot):
    bot.add_cog(Galaxy(bot))