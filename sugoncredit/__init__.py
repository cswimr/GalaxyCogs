from .sugoncredit import SugonCredit


async def setup(bot):
    await bot.add_cog(SugonCredit(bot))
