async def stand_callback(interaction):
    """Handle the Stand button."""
    if interaction.user.id != ctx.author.id:
        await interaction.response.send_message("This is not your game!", ephemeral=True)
        return

    # Dealer's turn: The dealer must draw until their value is 17 or more
    while dealer_value < 17:
        dealer_hand.append(self.draw_card())
        dealer_value = self.calculate_hand_value([card[:-1] for card in dealer_hand])

    # Determine the result based on hand values
    result_embed = discord.Embed(title="🎲 Blackjack Result", color=discord.Color.green() if player_value > dealer_value else discord.Color.red())
    result_embed.add_field(name="Dealer's Hand", value=f"{' '.join(dealer_hand)} ({dealer_value})", inline=False)
    result_embed.add_field(name="Your Hand", value=f"{' '.join(player_hand)} ({player_value})", inline=False)

    if dealer_value > 21 or player_value > dealer_value:
        result_embed.add_field(name="Result", value="You win!", inline=False)
        winnings = bet
    elif player_value == dealer_value:
        result_embed.add_field(name="Result", value="It's a tie!", inline=False)
        winnings = 0
    else:
        result_embed.add_field(name="Result", value="You lose!", inline=False)
        winnings = -bet

    # Update user's balance
    self.update_user_balance(user_id, winnings)
    result_embed.add_field(name="Winnings", value=f"${winnings}", inline=True)
    result_embed.add_field(name="New Balance", value=f"${self.get_user_balance(user_id)}", inline=False)

    # Remove buttons after game ends
    await interaction.response.edit_message(embed=result_embed, view=None)
