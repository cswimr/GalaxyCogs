from .sugoncredit import SugonCredit


def setup(bot):
    bot.add_cog(SugonCredit(bot))
