import React from 'react';
import { TouchableOpacity, Image, Text, StyleSheet, View, Dimensions } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { theme } from '@/constants/theme';
import { Event, DEFAULT_EVENT_IMAGE } from '../types';

const { width } = Dimensions.get('window');
const CARD_MARGIN = theme.spacing.lg;
const CARD_WIDTH = (width - (CARD_MARGIN * 3)) / 2; // 2 columns with margins

interface EventCardProps {
  event: Event;
  onPress: () => void;
  variant?: 'grid' | 'featured';
  showOrganization?: boolean;
}

export const EventCard: React.FC<EventCardProps> = ({
  event,
  onPress,
  variant = 'grid',
  showOrganization = false,
}) => {
  const isFeatured = variant === 'featured';
  const imageUrl = event.image_url || DEFAULT_EVENT_IMAGE;

  return (
    <TouchableOpacity
      style={[
        styles.card,
        isFeatured ? styles.featuredCard : styles.gridCard,
      ]}
      onPress={onPress}
      activeOpacity={0.9}
    >
      <Image
        source={{ uri: imageUrl }}
        style={styles.image}
        resizeMode="cover"
      />
      <LinearGradient
        colors={['transparent', 'rgba(0,0,0,0.7)']}
        style={styles.gradient}
      >
        <View style={styles.content}>
          <Text style={styles.title} numberOfLines={2}>
            {event.title}
          </Text>
          {showOrganization && event.club_name && (
            <Text style={styles.organization} numberOfLines={1}>
              {event.club_name}
            </Text>
          )}
        </View>
      </LinearGradient>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  card: {
    borderRadius: theme.borderRadius.lg,
    overflow: 'hidden',
    backgroundColor: theme.colors.cardBackground,
    ...theme.shadows.sm,
  },
  gridCard: {
    width: CARD_WIDTH,
    height: CARD_WIDTH * 1.2,
    marginBottom: theme.spacing.lg,
  },
  featuredCard: {
    width: width - (CARD_MARGIN * 2),
    height: 200,
    marginBottom: theme.spacing.md,
  },
  image: {
    width: '100%',
    height: '100%',
    position: 'absolute',
  },
  gradient: {
    flex: 1,
    justifyContent: 'flex-end',
  },
  content: {
    padding: theme.spacing.md,
  },
  title: {
    fontSize: theme.fontSize.base,
    fontFamily: 'Inter_600SemiBold',
    color: theme.colors.white,
    marginBottom: theme.spacing.xs,
  },
  organization: {
    fontSize: theme.fontSize.sm,
    fontFamily: 'Inter_500Medium',
    color: theme.colors.white,
    opacity: 0.9,
  },
});